from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles

from parser import parse_ast
from complex import Complex
from core import eval_program, lookup, Loc
from signal import signal, SIGALRM, alarm

app = FastAPI()

class ProgramInput(BaseModel):
    program: str

@app.post("/run_program")
def run_program(data: ProgramInput):
    try:
        ast = parse_ast(data.program)
        
        env, state = eval_program(ast)

        complexes_json = {}

        for name, dval in env.items():
            if not isinstance(dval, Loc):
                continue

            try:
                value = state.store[dval.addr]

                if isinstance(value, Complex):
                    complexes_json[name] = {
                        "dimension": value.dimension,
                        "simplices": [list(s) for s in value.maximal_simplices],
                        "vertices": list(value.vertices),
                        "classes": {
                            k: list(v) for k, v in value.classes.items()
                        }
                    }
            except KeyError:
                continue

        return {
            "success": True,
            "complexes": complexes_json
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

app.mount("/", StaticFiles(directory="web/frontend"), name="frontend")