# The Problem

> *"Every journey of a thousand APIs begins with a single socket."*

## Why Start Here?

You have used Express. You have used Fastify. You have used Hono. You have `npm install`'d a hundred frameworks. You have written `app.get('/users', handler)` a thousand times and never stopped to ask: *what is `app`? What is `get`? What is `handler`?*

That is the problem this project solves. Not "build a server" — you have built a hundred. The problem is: **you have never built a server.** You have built an Express app. You have configured someone else's abstraction. The machine that actually accepts a TCP connection and speaks HTTP is hidden from you.

This project is the *un-hiding*.

## What Pain Is This Solving?

Imagine you are a new backend engineer. You join a team. Production is on fire. The server is returning 500s. You `console.log` the request and you see... what? You don't know what a request *is*. You don't know what a header *is*. You don't know why `res.end()` is mandatory. You are debugging a system whose internals are invisible to you.

**The pain: opacity.** Frameworks are beautiful, but they hide the truth. This project tears the curtain away.

After this project, when Express throws a 500, you will *know* — at the wire level — what is happening. When a CDN returns a 502, you will know what a 502 means, not because you memorized it, but because you wrote the code that produces one.

## The Deeper Problem: Building Intuition

You cannot reason about a system you have never seen the inside of. You can memorize "Express is a thin wrapper around `node:http`," but that sentence is empty unless you have written `node:http` yourself. Memory is not understanding.

Intuition is built by *construction*. When you write the code that produces a 200, the 200 becomes a thing you *made*, not a thing you *read about*. When you forget to call `res.end()`, the connection hangs and you *see* it. You will never forget it. That is the kind of knowledge you cannot get from documentation.

## What This Project Will *Not* Solve

This project will not teach you routing (project 02). It will not teach you JSON (project 03). It will not teach you body parsing (project 05). It will not teach you cookies (project 06). It will not teach you anything except: **a server is a function that takes a request and returns a response.** That is enough. That is the foundation on which everything else is built.

## The Question This Project Answers

> *"What is a server, really?"*

If you can answer that question in one sentence after this project, you are ready for project 02. If you cannot, stay here. Read [THOUGHT.md](./THOUGHT.md). Read [BUILD.md](./BUILD.md). Run the code. Change the code. Break the code. Repeat until the answer is obvious.

The answer, in case you want to know it now: *a server is a long-running program that listens for connections, and every time a connection arrives, it calls a function that knows how to turn the request into a response.*
