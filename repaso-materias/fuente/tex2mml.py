"""Conversor mínimo de un subconjunto de LaTeX a MathML (sin dependencias).
Soporta: \\frac, \\dfrac, \\sqrt, _ ^ ' , \\text, \\mathrm, \\left \\right, griegas,
operadores comunes, \\sum \\int con límites, números con coma decimal y \\, \\; \\quad."""
import html

GREEK = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'varepsilon': 'ε', 'epsilon': 'ε',
    'eta': 'η', 'theta': 'θ', 'lambda': 'λ', 'mu': 'μ', 'rho': 'ρ', 'sigma': 'σ', 'phi': 'φ',
    'varphi': 'φ', 'psi': 'ψ', 'omega': 'ω', 'Delta': 'Δ', 'Sigma': 'Σ', 'Phi': 'Φ', 'pi': 'π',
}
OPS = {
    'le': '≤', 'leq': '≤', 'ge': '≥', 'geq': '≥', 'cdot': '·', 'times': '×', 'approx': '≈',
    'to': '→', 'Rightarrow': '⇒', 'Leftrightarrow': '⇔', 'pm': '±', 'neq': '≠', 'll': '≪',
    'gg': '≫', 'lt': '<', 'gt': '>', 'infty': '∞', 'prime': '′',
}
BIG = {'sum': '∑', 'int': '∫'}
OPCHARS = set('+-=<>()[]/,;|·×≤≥≈→⇒±∑∫:!')
GREEKCH = set('αβγδεηθλμρσφψωΔΣΦπ')


class P:
    def __init__(self, s):
        self.s, self.i = s, 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else ''

    def skip_ws(self):
        while self.peek() in (' ', '\n', '\t') and self.peek() != '':
            self.i += 1

    def group(self):
        """contenido entre llaves -> lista de nodos"""
        self.skip_ws()
        if self.peek() != '{':
            a = self.atom()
            return [a] if a else []
        self.i += 1
        nodes = self.seq('}')
        self.i += 1
        return nodes

    def raw_group(self):
        self.skip_ws()
        assert self.peek() == '{', self.s[self.i:self.i + 20]
        depth, j = 0, self.i
        while True:
            c = self.s[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        txt = self.s[self.i + 1:j]
        self.i = j + 1
        return txt

    def seq(self, end=None):
        out = []
        while True:
            self.skip_ws()
            c = self.peek()
            if c == '' or (end and c == end):
                return out
            a = self.atom()
            if a is None:
                continue
            a = self.scripts(a)
            out.append(a)

    def scripts(self, base):
        prime = False
        sub = sup = None
        while True:
            c = self.peek()
            if c == "'":
                prime = True
                self.i += 1
            elif c == '_':
                self.i += 1
                sub = self.script_group()
            elif c == '^':
                self.i += 1
                sup = self.script_group()
            else:
                break
        if prime:
            sup = '<mo>′</mo>' + (sup or '')
            sup = '<mrow>%s</mrow>' % sup
        if sub and sup:
            return '<msubsup>%s%s%s</msubsup>' % (base, sub, sup)
        if sub:
            return '<msub>%s%s</msub>' % (base, sub)
        if sup:
            return '<msup>%s%s</msup>' % (base, sup)
        return base

    def script_group(self):
        self.skip_ws()
        if self.peek() == '{':
            # corridas de letras de 2+ caracteres en subíndices van rectas
            txt = self.raw_group()
            q = P(txt)
            q.scriptmode = True
            return '<mrow>%s</mrow>' % ''.join(q.seq())
        a = self.atom()
        return a

    def atom(self):
        c = self.peek()
        if c == '':
            return None
        if c == '\\':
            self.i += 1
            j = self.i
            while self.i < len(self.s) and self.s[self.i].isalpha():
                self.i += 1
            cmd = self.s[j:self.i]
            if cmd == '':  # \, \; \! \{ etc
                ch = self.s[self.i]
                self.i += 1
                if ch == ',':
                    return '<mspace width="0.17em"/>'
                if ch == ';':
                    return '<mspace width="0.28em"/>'
                if ch == '!':
                    return None
                if ch in '{}':
                    return '<mo>%s</mo>' % ch
                if ch == ' ':
                    return '<mspace width="0.25em"/>'
                return '<mo>%s</mo>' % html.escape(ch)
            if cmd in ('frac', 'dfrac'):
                n = self.group()
                d = self.group()
                return '<mfrac><mrow>%s</mrow><mrow>%s</mrow></mfrac>' % (''.join(n), ''.join(d))
            if cmd == 'sqrt':
                x = self.group()
                return '<msqrt>%s</msqrt>' % ''.join(x)
            if cmd == 'text':
                t = self.raw_group()
                return '<mtext>%s</mtext>' % html.escape(t).replace(' ', ' ')
            if cmd == 'mathrm':
                t = self.raw_group()
                return '<mi mathvariant="normal">%s</mi>' % html.escape(t)
            if cmd in ('left', 'right'):
                self.skip_ws()
                ch = self.s[self.i]
                self.i += 1
                if ch == '.':
                    return None
                return '<mo stretchy="true">%s</mo>' % html.escape(ch)
            if cmd == 'quad':
                return '<mspace width="1em"/>'
            if cmd == 'qquad':
                return '<mspace width="2em"/>'
            if cmd in GREEK:
                return '<mi>%s</mi>' % GREEK[cmd]
            if cmd in OPS:
                return '<mo>%s</mo>' % OPS[cmd]
            if cmd in BIG:
                return '<mo largeop="true">%s</mo>' % BIG[cmd]
            if cmd == 'bar':
                x = self.group()
                return '<mover accent="true"><mrow>%s</mrow><mo>¯</mo></mover>' % ''.join(x)
            raise ValueError('comando desconocido: \\' + cmd)
        if c == '{':
            return '<mrow>%s</mrow>' % ''.join(self.group())
        if c.isdigit():
            j = self.i
            while self.i < len(self.s) and (self.s[self.i].isdigit() or
                                            (self.s[self.i] in ',.' and self.i + 1 < len(self.s)
                                             and self.s[self.i + 1].isdigit())):
                self.i += 1
            return '<mn>%s</mn>' % self.s[j:self.i]
        if c.isalpha() and c not in GREEKCH:
            if getattr(self, 'scriptmode', False):
                j = self.i
                while self.i < len(self.s) and self.s[self.i].isalpha() and self.s[self.i] not in GREEKCH:
                    self.i += 1
                w = self.s[j:self.i]
                if len(w) > 1:
                    return '<mi mathvariant="normal">%s</mi>' % w
                return '<mi>%s</mi>' % w
            self.i += 1
            return '<mi>%s</mi>' % c
        if c in GREEKCH:
            self.i += 1
            return '<mi>%s</mi>' % c
        self.i += 1
        if c == '-':
            return '<mo>−</mo>'
        if c == '*':
            return '<mo>·</mo>'
        if c in '()[]|':
            return '<mo stretchy="false">%s</mo>' % c
        if c == '<':
            return '<mo>&lt;</mo>'
        if c == '>':
            return '<mo>&gt;</mo>'
        return '<mo>%s</mo>' % html.escape(c)


def m(tex, block=False):
    body = ''.join(P(tex).seq())
    if block:
        return '<math display="block"><mrow>%s</mrow></math>' % body
    return '<math><mrow>%s</mrow></math>' % body


if __name__ == '__main__':
    print(m(r"M_n = A_s f_y \left(d - \frac{a}{2}\right) = A_s f_y d\,(1 - 0,59\, f_r \rho)", True))
    print(m(r"f'_c \ge \rho_{min} \quad \varepsilon_{cu}=0,003 \quad \sum T_{si} d_i^t"))
