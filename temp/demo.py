import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    import math
    import re


@app.function
#| no_doc

def greet(
    n:str="Mike"    # subject name
) -> str:           # greeting message
    "Construct a simple greeting"
    return print(f"Hi {n}; What is up?")


@app.cell
def _():
    greet()
    return


@app.cell
def _():
    greet("stranger")
    return


@app.cell
def _():
    greet("Alice")
    return


@app.function
def shout(f): return lambda *args,**kwargs: f(*args,**kwargs).upper()


@app.function
#| no_doc 

# But we still want to be able to have normal comments here if we want.. 

@shout
def greet2(n="Mike"): return f"Hi {n}; What is up?"


@app.cell
def _():
    greet("Alice")
    return


@app.cell
def _():
    greet2("Alice")
    return


@app.class_definition
#| nodoc


class FastPoint:
    "A 2D point with `x` and `y` coordinates"
    def __init__(self,
        x:float=0, # x coordinate
        y:float=0, # y coordinate
    ): self.x,self.y = x,y

    def distance_to(self,
        other, # Other FastPoint
    )->float: # Euclidean distance
        "Calculate Euclidean distance to `other` point"
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)

    def scale(self,
        factor:float, # Scaling factor
    ): # Returns self for chaining
        "Scale point by `factor` (mutates in place for efficiency)"
        self.x,self.y = self.x*factor,self.y*factor
        return self

    def __repr__(self
                )->str: # String representation
        return f"FastPoint({self.x}, {self.y})"

    def __add__(self,
        o, # Other FastPoint
    ): # Sum of points
        return FastPoint(self.x+o.x, self.y+o.y)

    def __mul__(self,
        n:float, # Scaling factor
    ): # Scaled point
        return FastPoint(self.x*n, self.y*n)


@app.cell
def _():
    #| just a normal cell here 
    p1 = FastPoint(3, 4)
    p2 = FastPoint(0, 0)
    print(p1)
    print(f"Distance from origin: {p1.distance_to(p2)}")
    print(f"Scaled: {p1.scale(2)}")
    print(f"Sum: {FastPoint(1,2) + FastPoint(3,4)}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
