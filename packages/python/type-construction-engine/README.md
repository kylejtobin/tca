# type-construction-engine

Reads a program's classes, proves them at startup, and answers a route by construction: each pass asks Pydantic for every class not yet built from the instances its fields name, performs the actions that constructed, and stops when the route itself constructs. One span per answer, one per performed action.
