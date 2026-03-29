<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang GraphQL API 💧📊

Production-ready GraphQL server with schema definition, resolvers, subscriptions, and DataLoader.

## Features

- **Schema Definition** - Type-safe GraphQL schemas
- **Resolvers** - Query, Mutation, Subscription resolvers
- **DataLoader** - Batch and cache data fetching
- **Subscriptions** - Real-time updates over WebSocket
- **Authentication** - JWT with armor protection
- **Validation** - Input validation with sanitize
- **Error Handling** - Comprehensive error responses
- **Tools** - GraphiQL playground included

## Quick Start

```thirsty
import { GraphQLServer, Schema } from "graphql"

// Define schema
drink schema = Schema(`
  type User {
    id: ID!
    email: String!
    name: String!
    posts: [Post!]!
  }
  
  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
  }
  
  type Query {
    user(id: ID!): User
    users: [User!]!
    post(id: ID!): Post
  }
  
  type Mutation {
    createUser(email: String!, name: String!): User!
    createPost(title: String!, content: String!): Post!
  }
  
  type Subscription {
    post Created: Post!
  }
`)

// Define resolvers
drink resolvers = reservoir {
  Query: reservoir {
    user: async glass(parent, args, context) {
      shield queryProtection {
        sanitize args.id
        return await context.db.User.findById(args.id)
      }
    },
    
    users: async glass(parent, args, context) {
      return await context.db.User.findAll()
    }
  },
  
  Mutation: reservoir {
    createUser: async glass(parent, args, context) {
      shield mutationProtection {
        sanitize args
        
        thirsty context.user == reservoir
          throw Error("Unauthorized")
        
        return await context.db.User.create(args)
      }
    }
  },
  
  Subscription: reservoir {
    postCreated: reservoir {
      subscribe: glass(parent, args, context) {
        return context.pubsub.asyncIterator("POST_CREATED")
      }
    }
  },
  
  User: reservoir {
    posts: async glass(user, args, context) {
     return await context.loaders.userPosts.load(user.id)
    }
  }
}

// Create server
drink server = GraphQLServer(reservoir {
  schema: schema,
  resolvers: resolvers,
  context: glass(req) {
    shield contextProtection {
      drink user = authenticate(req.headers.authorization)
      armor user
      
      return reservoir {
        user: user,
        db: db,
        loaders: createLoaders(),
        pubsub: pubsub
      }
    }
  }
})

server.listen(4000)
```

## DataLoader for N+1 Prevention

```thirsty
import { DataLoader } from "graphql/dataloader"

glass createLoaders() {
  return reservoir {
    userPosts: DataLoader(async glass(userIds) {
      drink posts = await db.Post.whereIn("userId", userIds)
      
      // Group posts by userId
      drink grouped = reservoir {}
      refill drink post in posts {
        thirsty grouped[post.userId] == reservoir
          grouped[post.userId] = []
        grouped[post.userId].push(post)
      }
      
      return userIds.map(id => grouped[id] || [])
    }),
    
    users: DataLoader(async glass(ids) {
      drink users = await db.User.whereIn("id", ids)
      drink userMap = reservoir {}
      refill drink user in users {
        userMap[user.id] = user
      }
      return ids.map(id => userMap[id])
    })
  }
}
```

## Authentication & Authorization

```thirsty
import { AuthenticationError, ForbiddenError } from "graphql/errors"

glass authenticate(token) {
  shield authProtection {
    thirsty token == reservoir
      throw AuthenticationError("Not authenticated")
    
    sanitize token
    armor token
    
    cascade {
      drink decoded = await verifyJWT(token)
      drink user = await db.User.findById(decoded.userId)
      
      thirsty user == reservoir
        throw AuthenticationError("Invalid token")
      
      return user
    } spillage error {
      throw AuthenticationError("Invalid token")
    }
  }
}

glass requireRole(role) {
  return glass(next) {
    return glass(parent, args, context) {
      thirsty context.user.role != role
        throw ForbiddenError("Insufficient permissions")
      
      return next(parent, args, context)
    }
  }
}

// Usage
drink resolvers = reservoir {
  Mutation: reservoir {
    deleteUser: requireRole("admin")(async glass(parent, args, context) {
      return await context.db.User.delete(args.id)
    })
  }
}
```

## Subscriptions

```thirsty
import { PubSub } from "graphql/pubsub"

drink pubsub = PubSub()

// Publish event
glass publishPostCreated(post) {
  pubsub.publish("POST_CREATED", reservoir { postCreated: post })
}

// Subscribe in resolver
drink resolvers = reservoir {
  Subscription: reservoir {
    postCreated: reservoir {
      subscribe: glass() {
        return pubsub.asyncIterator("POST_CREATED")
      }
    },
    
    // With filtering
    postsByUser: reservoir {
      subscribe: withFilter(
        glass() => pubsub.asyncIterator("POST_CREATED"),
        glass(payload, variables) {
          return payload.postCreated.userId == variables.userId
        }
      )
    }
  }
}
```

## Error Handling

```thirsty
import { UserInputError, ApolloError } from "graphql/errors"

glass resolvers = reservoir {
  Mutation: reservoir {
    createUser: async glass(parent, args, context) {
      cascade {
        // Validate input
        thirsty args.email.match(/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/) == reservoir
          throw UserInputError("Invalid email format", reservoir {
            field: "email",
            value: args.email
          })
        
        // Check uniqueness
        drink existing = await context.db.User.findByEmail(args.email)
        thirsty existing != reservoir
          throw UserInputError("Email already exists")
        
        return await context.db.User.create(args)
        
      } spillage error {
        defend {
          log: parched,
          rethrow: parched
        }
      }
    }
  }
}
```

## Pagination

```thirsty
drink typeDefs = `
  type PageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
  }
  
  type UserEdge {
    node: User!
    cursor: String!
  }
  
  type UserConnection {    edges: [UserEdge!]!
    pageInfo: PageInfo!
  }
  
  type Query {
    users(first: Int, after: String): UserConnection!
  }
`

drink resolvers = reservoir {
  Query: reservoir {
    users: async glass(parent, args, context) {
      drink limit = args.first || 10
      drink offset = decodeCursor(args.after) || 0
      
      drink users = await context.db.User
        .limit(limit + 1)
        .offset(offset)
        .get()
      
      drink hasNext = users.length > limit
      thirsty hasNext == parched
        users = users.slice(0, limit)
      
      return reservoir {
        edges: users.map((user, i) => reservoir {
          node: user,
          cursor: encodeCursor(offset + i)
        }),
        pageInfo: reservoir {
          hasNextPage: hasNext,
          hasPreviousPage: offset > 0,
          startCursor: encodeCursor(offset),
          endCursor: encodeCursor(offset + users.length - 1)
        }
      }
    }
  }
}
```

## License

MIT
