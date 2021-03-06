import re
import sympy

from colorama import Fore
from six.moves import input

from plugin import alias, plugin


@plugin()
@alias('calc', 'evaluate')
def calculate(jarvis, s):
    """
    Jarvis will get your calculations done!
    -- Example:
        calculate 3 + 5
    """

    tempt = s.replace(" ", "")
    if len(tempt) > 1:
        calc(jarvis, tempt)
    else:
        jarvis.say("Error: Not in correct format", Fore.RED)


@plugin()
def solve(jarvis, s):
    """
    Prints where expression equals zero
    -- Example:
        solve x**2 + 5*x + 3
        solve x + 3 = 5
    """
    x = sympy.Symbol('x')

    def _format(solutions):
        if solutions == 0:
            return "No solution!"
        ret = ''
        for count, point in enumerate(solutions):
            if x not in point:
                return "Please use 'x' in expression."
            x_value = point[x]
            ret += "{}. x: {}\n".format(count, x_value)
        return ret

    def _calc(expr):
        return sympy.solve(expr, x, dict=True)

    s = remove_equals(jarvis, s)
    calc(jarvis, s, calculator=_calc, formatter=_format)


@plugin()
def equations(jarvis, term):
    """
    Solves linear equations system

    Use variables: a, b, c, ..., x, y,z

    Example:

    ~> Hi, what can I do for you?
    equations
    1. Equation: x**2 + 2y - z = 6
    2. Equation: (x-1)(y-1) = 0
    3. Equation: y**2 - x -10 = y**2 -y
    4. Equation:
    [{x: -9, y: 1, z: 77}, {x: 1, y: 11, z: 17}]

    """
    a, b, c, d, e, f, g, h, i, j, k, l, m = sympy.symbols('a,b,c,d,e,f,g,h,i,j,k,l,m')
    n, o, p, q, r, s, t, u, v, w, x, y, z = sympy.symbols('n,o,p,q,r,s,t,u,v,w,x,y,z')

    equations = []
    count = 1
    user_input = input('{}. Equation: '.format(count))
    while user_input != '':
        count += 1
        user_input = format_expression(user_input)
        user_input = remove_equals(jarvis, user_input)
        equations.append(user_input)
        user_input = input('{}. Equation: '.format(count))

    calc(jarvis, term, calculator=lambda expr: sympy.solve(equations, dict=True))


@plugin()
def factor(jarvis, s):
    """
    Jarvis will factories
    -- Example:
        factor x**2-y**2
    """
    tempt = s.replace(" ", "")
    if len(tempt) > 1:
        calc(jarvis, tempt, formatter=sympy.factor)
    else:
        jarvis.say("Error: Not in correct format", Fore.RED)


@plugin()
@alias("curve plot")
def plot(jarvis, s):
    """
    Plot graph
    -- Example:
        plot x**2
        plot y=x(x+1)(x-1)
    """
    def _plot(expr):
        sympy.plotting.plot(expr)
        return ""

    s = remove_equals(jarvis, s)
    calc(jarvis, s, calculator=solve_y, formatter=_plot)


@plugin()
def limit(jarvis, s):
    """
    Prints limit to +/- infinity or to number +-. Use 'x' as variable.
    -- Examples:
        limit 1/x
        limit @1 1/(1-x)
        limit @1 @2 1/((1-x)(2-x))
    """
    def try_limit(term, x, to, directory=''):
        try:
            return sympy.Limit(term, x, to, directory).doit()
        except sympy.SympifyError:
            return 'Error'


    s_split = s.split()
    limit_to = []
    term = ""
    for token in s_split:
        if token[0] == '@':
            if token[1:].isnumeric():
                limit_to.append(int(token[1:]))
            else:
                jarvis.say("Error: {} Not a number".format(token[1:]), Fore.RED)
        else:
            term += token

    term = remove_equals(jarvis, term)
    term = format_expression(term)
    term = solve_y(term)

    x = sympy.Symbol('x')


    # infinity:
    jarvis.say("lim ->  ∞\t= {}".format(try_limit(term, x, +sympy.S.Infinity)), Fore.BLUE)
    jarvis.say("lim -> -∞\t= {}".format(try_limit(term, x, -sympy.S.Infinity)), Fore.BLUE)

    for limit in limit_to:
        limit_plus = try_limit(term, x, limit, dir="+")
        limit_minus = try_limit(term, x, limit, dir="-")

        jarvis.say("lim -> {}(+)\t= {}".format(limit, limit_plus), Fore.BLUE)
        jarvis.say("lim -> {}(-)\t= {}".format(limit, limit_minus), Fore.BLUE)


def remove_equals(jarvis, equation):
    """
    User should be able to input equations like x + y = 1.
    SymPy only accepts equations like: x + y - 1 = 0.
    => This method Finds '=' and move everything beyond to left side
    """
    split = equation.split('=')
    if len(split) == 1:
        return equation
    if len(split) != 2:
        jarvis.say("Warning! More than one = detected!", Fore.RED)
        return equation

    return "{} - ({})".format(split[0], split[1])


def format_expression(s):
    s = str.lower(s)
    s = s.replace("power", "**")
    s = s.replace("plus", "+")
    s = s.replace("minus", "-")
    s = s.replace("divided by", "/")
    s = s.replace("by", "/")
    s = s.replace("^", "**")

    # Insert missing * commonly omitted
    # 2x -> 2*x
    p = re.compile('(\d+)([abcxyz])')
    s = p.sub(r'\1*\2', s)

    # x(... -> x*(...
    p = re.compile('([abcxyz])\(')
    s = p.sub(r'\1*(', s)

    # (x-1)(x+1) -> (x-1)*(x+1)
    # x(... -> x*(...
    s = s.replace(")(", ")*(")

    return s


def solve_y(s):
        if 'y' in s:
            y = sympy.Symbol('y')
            results = sympy.solve(s, y)
            if len(results) == 0:
                return '0'
            else:
                return results[0]
        else:
            return solve_y("({}) -y".format(s))


def calc(jarvis, s, calculator=sympy.sympify, formatter=None):
    s = format_expression(s)
    try:
        result = calculator(s)
    except sympy.SympifyError:
        jarvis.say("Error: Something is wrong with your expression", Fore.RED)
        return

    if formatter is not None:
        result = formatter(result)

    jarvis.say(str(result), Fore.BLUE)


@plugin()
@alias("curve sketch")
def curvesketch(jarvis, s):
    """
    Prints useful information about a graph of a function.
    * Limit
    * Intersection x/y axis
    * Derivative and Integral
    * Minima / Maxima / Turning point
    -- Example:
        curve sketch x**2+10x-5
        curve sketch y=sqrt((x+1)(x-1))
        curve sketch y=1/3x**3-2x**2+3x
    """
    def section(jarvis, headline):
        jarvis.say("\n{:#^50}".format(" {} ".format(headline)), Fore.MAGENTA)


    term = remove_equals(jarvis, s)
    term = format_expression(term)
    term = solve_y(term)


    def get_y(x_val, func=term):
        x = sympy.Symbol('x')
        return func.evalf(subs={x: x_val})

    section(jarvis, s)

    section(jarvis, "Graph")
    plot().run(jarvis, s)

    section(jarvis, "Limit")
    limit().run(jarvis, str(term))

    section(jarvis, "Intersection x-axis")
    solve().run(jarvis, str(term))

    section(jarvis, "Intersection y-axis")
    jarvis.say(str(get_y(0).round(9)), Fore.BLUE)

    section(jarvis, "Factor")
    factor().run(jarvis, str(term))

    section(jarvis, "Derivative")
    x = sympy.Symbol('x')
    derivative_1 = sympy.Derivative(term, x).doit()
    derivative_2 = sympy.Derivative(derivative_1, x).doit()
    derivative_3 = sympy.Derivative(derivative_2, x).doit()
    jarvis.say("1. Derivative: {}".format(derivative_1), Fore.BLUE)
    jarvis.say("2. Derivative: {}".format(derivative_2), Fore.BLUE)
    jarvis.say("3. Derivative: {}".format(derivative_3), Fore.BLUE)

    section(jarvis, "Integral")
    jarvis.say("F(x) = {} + t".format(sympy.Integral(term, x).doit()), Fore.BLUE)

    section(jarvis, "Maxima / Minima")
    critical_points = sympy.solve(derivative_1)

    for x in critical_points:
        y = str(get_y(x).round(9))

        try:
            isminmax = float(get_y(x, func=derivative_2))
        except ValueError:
            isminmax = 0

        if isminmax > 0:
            minmax = "Minima"
        elif isminmax < 0:
            minmax = "Maxima"
        else:
            minmax = "/"

        jarvis.say("({}/{}) : {}".format(x, y, minmax), Fore.BLUE)

    section(jarvis, "Turning Point")
    critical_points = sympy.solve(derivative_2)

    for x in critical_points:
        y = get_y(x)

        try:
            is_turning_point = float(get_y(x, func=derivative_3))
        except ValueError:
            is_turning_point = -1

        if is_turning_point != 0:
            jarvis.say("({}/{})".format(x, y.round(9)), Fore.BLUE)

    section(jarvis, "")
