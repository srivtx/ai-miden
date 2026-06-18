// __tests__/api.test.js
//
// Vitest + supertest + a fresh in-memory SQLite for each test file.
// We override the database connection in the module under test, run migrations
// once, then exercise the API end-to-end without binding a port.
//
// Run: npx vitest run

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import request from "supertest";
import knexLib from "knex";

// Use an in-memory DB for the whole test process
process.env.DATABASE_URL = ":memory:";
process.env.STRIPE_SECRET_KEY = "sk_test_dummy";
process.env.STRIPE_WEBHOOK_SECRET = "whsec_dummy";

// Import AFTER env vars are set
const { app, db, migrate, SECRET } = await import("../server.js");

let aliceToken;
let aliceId;
let bobToken;
let bobId;

beforeAll(async () => {
  await migrate();
  // Alice
  const alice = await request(app)
    .post("/users")
    .send({ username: "alice", password: "password123", email: "alice@example.com" });
  expect(alice.status).toBe(201);
  aliceId = alice.body.id;
  // Bob
  const bob = await request(app)
    .post("/users")
    .send({ username: "bob", password: "password123", email: "bob@example.com" });
  expect(bob.status).toBe(201);
  bobId = bob.body.id;
  // Tokens
  const aliceSession = await request(app)
    .post("/sessions")
    .send({ username: "alice", password: "password123" });
  expect(aliceSession.status).toBe(201);
  aliceToken = aliceSession.body.token;
  const bobSession = await request(app)
    .post("/sessions")
    .send({ username: "bob", password: "password123" });
  bobToken = bobSession.body.token;
});

afterAll(async () => {
  await db.destroy();
});

describe("auth", () => {
  it("rejects missing token on protected route", async () => {
    const res = await request(app).get("/sessions/me");
    expect(res.status).toBe(401);
    expect(res.body.code).toBe("UNAUTHORIZED");
  });
  it("returns 401 for bad credentials", async () => {
    const res = await request(app)
      .post("/sessions")
      .send({ username: "alice", password: "wrong" });
    expect(res.status).toBe(401);
  });
  it("issues a JWT on correct credentials", async () => {
    const res = await request(app)
      .post("/sessions")
      .send({ username: "alice", password: "password123" });
    expect(res.status).toBe(201);
    expect(res.body.token).toBeDefined();
  });
});

describe("validation", () => {
  it("rejects too-short username", async () => {
    const res = await request(app)
      .post("/users")
      .send({ username: "ab", password: "password123" });
    expect(res.status).toBe(400);
    expect(res.body.code).toBe("VALIDATION");
  });
  it("rejects too-short password", async () => {
    const res = await request(app)
      .post("/users")
      .send({ username: "charlie", password: "short" });
    expect(res.status).toBe(400);
  });
  it("rejects invalid email", async () => {
    const res = await request(app)
      .post("/users")
      .send({ username: "dave", password: "password123", email: "not-an-email" });
    expect(res.status).toBe(400);
  });
});

describe("user CRUD", () => {
  it("lists users with pagination meta", async () => {
    const res = await request(app).get("/users?limit=10");
    expect(res.status).toBe(200);
    expect(res.body.meta).toBeDefined();
    expect(res.body.meta.total).toBeGreaterThanOrEqual(2);
    expect(Array.isArray(res.body.data)).toBe(true);
  });
  it("gets a single user", async () => {
    const res = await request(app).get(`/users/${aliceId}`);
    expect(res.status).toBe(200);
    expect(res.body.username).toBe("alice");
  });
  it("returns 404 for unknown user", async () => {
    const res = await request(app).get("/users/99999");
    expect(res.status).toBe(404);
  });
  it("patches own user", async () => {
    const res = await request(app)
      .patch(`/users/${aliceId}`)
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ email: "alice2@example.com" });
    expect(res.status).toBe(200);
    expect(res.body.email).toBe("alice2@example.com");
  });
  it("rejects patch of another user", async () => {
    const res = await request(app)
      .patch(`/users/${bobId}`)
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ email: "evil@example.com" });
    expect(res.status).toBe(403);
  });
});

describe("posts", () => {
  let postId;
  it("creates a post", async () => {
    const res = await request(app)
      .post("/posts")
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ title: "Hello", body: "World" });
    expect(res.status).toBe(201);
    expect(res.body.title).toBe("Hello");
    postId = res.body.id;
  });
  it("gets the post", async () => {
    const res = await request(app).get(`/posts/${postId}`);
    expect(res.status).toBe(200);
    expect(res.body.author).toBe("alice");
  });
  it("patches own post", async () => {
    const res = await request(app)
      .patch(`/posts/${postId}`)
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ title: "Updated" });
    expect(res.status).toBe(200);
    expect(res.body.title).toBe("Updated");
  });
  it("forbids patching another user's post", async () => {
    const res = await request(app)
      .patch(`/posts/${postId}`)
      .set("Authorization", `Bearer ${bobToken}`)
      .send({ title: "Hacked" });
    expect(res.status).toBe(403);
  });
  it("deletes own post", async () => {
    const res = await request(app)
      .delete(`/posts/${postId}`)
      .set("Authorization", `Bearer ${aliceToken}`);
    expect(res.status).toBe(204);
  });
});

describe("transfer", () => {
  beforeAll(async () => {
    await db("users").where({ id: aliceId }).update({ balance: 1000 });
    await db("users").where({ id: bobId }).update({ balance: 0 });
  });
  it("transfers funds", async () => {
    const res = await request(app)
      .post("/transfer")
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ fromUserId: aliceId, toUserId: bobId, amount: 100 });
    expect(res.status).toBe(200);
    const alice = await db("users").where({ id: aliceId }).first();
    const bob = await db("users").where({ id: bobId }).first();
    expect(alice.balance).toBe(900);
    expect(bob.balance).toBe(100);
  });
  it("rejects transfer from another user", async () => {
    const res = await request(app)
      .post("/transfer")
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ fromUserId: bobId, toUserId: aliceId, amount: 50 });
    expect(res.status).toBe(403);
  });
  it("rejects insufficient funds", async () => {
    const res = await request(app)
      .post("/transfer")
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ fromUserId: aliceId, toUserId: bobId, amount: 999999 });
    expect(res.status).toBe(400);
  });
});

describe("workspaces + RBAC", () => {
  let workspaceId;
  it("alice creates a workspace", async () => {
    const res = await request(app)
      .post("/workspaces")
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ name: "ACME" });
    expect(res.status).toBe(201);
    workspaceId = res.body.id;
  });
  it("alice can read the workspace", async () => {
    const res = await request(app)
      .get(`/workspaces/${workspaceId}`)
      .set("Authorization", `Bearer ${aliceToken}`);
    expect(res.status).toBe(200);
  });
  it("bob cannot read the workspace (not a member)", async () => {
    const res = await request(app)
      .get(`/workspaces/${workspaceId}`)
      .set("Authorization", `Bearer ${bobToken}`);
    expect(res.status).toBe(403);
  });
  it("alice adds bob as a member", async () => {
    const res = await request(app)
      .post(`/workspaces/${workspaceId}/members`)
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ userId: bobId, role: "member" });
    expect(res.status).toBe(201);
  });
  it("bob can now read the workspace", async () => {
    const res = await request(app)
      .get(`/workspaces/${workspaceId}`)
      .set("Authorization", `Bearer ${bobToken}`);
    expect(res.status).toBe(200);
  });
  it("bob (member) cannot add a new member (admin required)", async () => {
    // Need a third user to test add — but for now we check the 403 path
    const res = await request(app)
      .post(`/workspaces/${workspaceId}/members`)
      .set("Authorization", `Bearer ${bobToken}`)
      .send({ userId: aliceId, role: "guest" });
    expect(res.status).toBe(403);
  });
});

describe("webhooks", () => {
  it("alice creates a webhook", async () => {
    const res = await request(app)
      .post("/webhooks")
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ url: "https://example.com/hook", events: ["post.created"] });
    expect(res.status).toBe(201);
    expect(res.body.secret).toMatch(/^whsec_/);
  });
  it("lists alice's webhooks", async () => {
    const res = await request(app)
      .get("/webhooks")
      .set("Authorization", `Bearer ${aliceToken}`);
    expect(res.status).toBe(200);
    expect(res.body.data.length).toBeGreaterThan(0);
  });
  it("rejects bad URL", async () => {
    const res = await request(app)
      .post("/webhooks")
      .set("Authorization", `Bearer ${aliceToken}`)
      .send({ url: "not-a-url", events: ["post.created"] });
    expect(res.status).toBe(400);
  });
});
