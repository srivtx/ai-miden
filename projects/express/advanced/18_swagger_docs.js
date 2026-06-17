// 18_swagger_docs.js — OpenAPI/Swagger documentation with swagger-jsdoc + swagger-ui-express.
const express = require('express');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const app = express();
app.use(express.json());

const options = {
  definition: {
    openapi: '3.0.0',
    info: { title: 'User API', version: '1.0.0', description: 'A sample user management API' },
    servers: [{ url: 'http://localhost:3000', description: 'Development' }],
    components: {
      securitySchemes: { bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' } },
      schemas: {
        User: { type: 'object', required: ['name', 'email'], properties: { id: { type: 'integer' }, name: { type: 'string' }, email: { type: 'string', format: 'email' }, role: { type: 'string', enum: ['user', 'admin'] }, createdAt: { type: 'string', format: 'date-time' } } },
        Error: { type: 'object', properties: { code: { type: 'string' }, message: { type: 'string' } } },
      },
    },
  },
  apis: [__filename], // scan this file for JSDoc comments
};

const swaggerSpec = swaggerJsdoc(options);
app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

const users = [];

/**
 * @openapi
 * /users:
 *   get:
 *     summary: List all users
 *     tags: [Users]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema: { type: integer, default: 1 }
 *       - in: query
 *         name: limit
 *         schema: { type: integer, default: 10 }
 *     responses:
 *       200:
 *         description: Paginated user list
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 total: { type: integer }
 *                 page: { type: integer }
 *                 data: { type: array, items: { $ref: '#/components/schemas/User' } }
 */
app.get('/users', (req, res) => {
  res.json({ total: users.length, page: 1, data: users });
});

/**
 * @openapi
 * /users:
 *   post:
 *     summary: Create a user
 *     tags: [Users]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [name, email]
 *             properties:
 *               name: { type: string }
 *               email: { type: string, format: email }
 *     responses:
 *       201: { description: User created }
 *       400: { description: Validation error }
 */
app.post('/users', (req, res) => {
  const user = { id: users.length + 1, ...req.body, createdAt: new Date().toISOString() };
  users.push(user);
  res.status(201).json(user);
});

app.listen(3000, () => console.log('Docs at http://localhost:3000/docs'));
