from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles

from parser import parse_ast
from core import Complex, eval_program, lookup

app = FastAPI()

class ProgramInput(BaseModel):
    program: str


@app.post("/run_program")
def run_program(data: ProgramInput):
    try:
        ast = parse_ast(data.program)
        env = eval_program(ast)

        complexes_json = {}

        for name in env.keys():
            try:
                c = lookup(env, name)
                print(c)
                if(isinstance(c, Complex)):
                    complexes_json[name] = {
                        "dimension": c.dimension,
                        "simplices": [list(s) for s in c.maximal_simplices],
                        "vertices": list(c.vertices),
                        "classes": {k: list(v) for k, v in c.classes.items()}
                    }
            except Exception:
                pass

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
