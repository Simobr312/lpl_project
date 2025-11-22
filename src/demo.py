from main import *

def demo():
    src = '''
    complex S1 = [A, B, C]
    complex S2 = [D, E, F]
    complex U = union(S1, S2)
    complex G = glue(S1, S2) mapping {B -> E, C -> F}
    '''
    ast = parse_ast(src)
    env = eval_program(ast)

    for name in ['S1', 'S2', 'U', 'G']:
        c = lookup(env, name)
        print(f"{name}: {c}")

    # quick sanity tests
    s1 = lookup(env, 'S1')
    assert s1.dimension == 2
    s2 = lookup(env, 'S2')
    assert s2.dimension == 2
    u = lookup(env, 'U')
    assert u.dimension == 2
    g = lookup(env, 'G')
    # after gluing B->E and C->F the glued complex still has a 2-simplex
    assert any(len(s) == 3 for s in g.maximal_simplices)

    # Tests for semantic checks
    try:
        # illegal union: using same vertex name across declarations (will raise earlier at declaration time)
        src2 = '''
        complex X = [A, X1]
        complex Y = [A, Y1]
        complex BAD = union(X, Y)
        '''
        ast2 = parse_ast(src2)
        eval_program(ast2)
    except ValueError as e:
        print('\nExpected error (duplicate vertex across declarations):', e)

    try:
        # illegal glue: mapping refers to missing vertex
        src3 = '''
        complex P = [P1, P2]
        complex Q = [Q1, Q2]
        complex BADG = glue(P, Q) mapping {P3 -> Q1}
        '''
        ast3 = parse_ast(src3)
        eval_program(ast3)
    except ValueError as e:
        print('\nExpected error (mapping key not found):', e)

    try:
        # illegal glue: non-injective mapping
        src4 = '''
        complex R = [R1, R2]
        complex S = [S1, S2]
        complex BADG2 = glue(R, S) mapping {R1 -> S1, R2 -> S1}
        '''
        ast4 = parse_ast(src4)
        eval_program(ast4)
    except ValueError as e:
        print('\nExpected error (non-injective mapping):', e)

    print('\nAll quick checks passed.')

if __name__ == '__main__':
    demo()