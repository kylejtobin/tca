---
name: tca-infra
description: "How a TCA project is built, checked and run: one entry point, every action in a container, everything declared. Use before writing or changing a justfile, Dockerfile, compose.yaml, .env.example, pre-commit configuration or CI workflow, and whenever a recipe is about to be added."
---

# TCA Infra

Infrastructure is how the work happens, not a model of anything. It has no
nouns, no kinds and no loop. It shares TCA's foundation and none of its
shapes: declare what exists, give every input one source, leave nothing
hidden, and let correctness fall out of the declaration instead of being
checked for afterwards.

## The way

Three files, one entry point: a `justfile` names every action a person can
take, Docker declares the environment the action runs in, and Compose
declares the services around it. Every recipe runs in the container. The
machine you are on does not matter, and nothing happens that is not written
down. A stranger reads the three files and knows how the project works.

In a cloud, keep the principle and change the form: Pulumi, Terraform or
whichever tool declares that environment. The test for any tool is the same.
Remove every command; does what remains still say what runs? If what remains
is a script, nothing was declared.

## Declare, never script

Each rule below is one question asked of a line. Ask it of every line you
write, and of every line you are about to write around a problem.

- Is every input fixed by its content? Every image by version and digest, every
  dependency from the lockfile, installed in a layer of its own before the
  code. A moving tag is an input that changes under you.
- Does every input have exactly one source? Configuration enters only from the
  environment, and every variable it may hold is named in `.env.example`, empty
  where it is a secret. A value in two places is a value that will disagree.
- Is anything known only at run time inside the image? No secret, no deployment
  setting, no address. An image that knows its deployment is one image per
  deployment.
- Does the build see more than the image needs? The build context holds the
  code and its declarations, never `.git`, `.env`, a virtualenv or a cache.
- Does anything run as root? The container runs as the host's user, so a file
  it writes is the host's file.
- Is there a second way in? Every action is a recipe; a command a person types
  that is not a recipe is a step nobody else can repeat.

## What a recipe is for

The `justfile` is project administration: the things a person does to the
project. Build the image. Lock the dependencies. Run the checks. Open a shell.
Start the services. Nothing else.

A recipe is never a program's interface. Not a package's API, not a wrapper
around its command line, not a way to call one of its functions. The test:
delete the package; if the recipe's meaning goes with it, the recipe did not
belong in the `justfile`. A program is reached as its own contract says, by
its route, its command or its `run`, from the package that owns it.

## Checks

A check runs the same way everywhere or it is not a check. One recipe,
`check`, runs every check the project has, and that recipe is what a hook
runs before a commit lands and what CI runs on every push. There is one
definition of green, and it is the recipe.

What a project carries by default, because the cost of each is nothing and
the cost of its absence is found late: lint and format, type checking, the
project's own checks, dependency audit, static security analysis, and secret
detection. Put an agent in a hook where a judgment is worth automating, and
give it the artifact to judge, never an account of it.

## Done

A stranger with Docker and `just` clones the repository, runs `just build`
and `just check`, and gets the answer CI got. Until that is true, the
infrastructure is not done, whatever else works on your machine.

This repository's `justfile`, `Dockerfile`, `compose.yaml`, `.env.example` and
`.pre-commit-config.yaml` are the example. Read them where they live.
