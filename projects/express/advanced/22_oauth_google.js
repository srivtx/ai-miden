// 22_oauth_google.js — Google OAuth login with Passport.js.
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const app = express();

// Session (needed for OAuth state)
app.use(session({ secret: 'session-secret', resave: false, saveUninitialized: true }));
app.use(passport.initialize());
app.use(passport.session());

// In-memory user store
const users = {};

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID || 'YOUR_CLIENT_ID',
  clientSecret: process.env.GOOGLE_CLIENT_SECRET || 'YOUR_CLIENT_SECRET',
  callbackURL: 'http://localhost:3000/auth/google/callback',
}, (accessToken, refreshToken, profile, done) => {
  // Find or create user
  const id = profile.id;
  if (!users[id]) users[id] = { id, name: profile.displayName, email: profile.emails?.[0]?.value, avatar: profile.photos?.[0]?.value };
  done(null, users[id]);
}));

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => done(null, users[id]));

// Routes
app.get('/', (req, res) => {
  if (req.isAuthenticated()) return res.send(`<h1>Hello ${req.user.name}</h1><p>${req.user.email}</p><img src="${req.user.avatar}"><br><a href="/logout">Logout</a>`);
  res.send('<h1>Welcome</h1><a href="/auth/google">Login with Google</a>');
});

app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));
app.get('/auth/google/callback', passport.authenticate('google', { failureRedirect: '/' }), (req, res) => res.redirect('/'));
app.get('/logout', (req, res) => { req.logout(() => res.redirect('/')); });

// Protected API
app.get('/api/me', (req, res) => {
  if (!req.isAuthenticated()) return res.status(401).json({ error: 'Login required' });
  res.json(req.user);
});

app.listen(3000, () => console.log('OAuth :3000 (set GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET env vars)'));
