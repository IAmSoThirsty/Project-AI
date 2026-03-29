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

# Thirsty-lang Database ORM 💧🗄️

Production-ready Object-Relational Mapping framework with query builder, migrations, and relationships.

## Features

- **Query Builder** - Fluent SQL query construction  
- **Migrations** - Version-controlled schema changes
- **Relationships** - One-to-many, many-to-many, polymorphic
- **Transactions** - ACID-compliant with shield protection
- **Connection Pooling** - Efficient database connections
- **Multiple Databases** - PostgreSQL, MySQL, SQLite
- **Schema Builder** - Define schemas in Thirsty-lang
- **Soft Deletes** - Non-destructive record deletion

## Quick Start

```thirsty
import { Model, Schema, DB } from "orm"

// Define model
glass User extends Model {
  drink schema = Schema(reservoir {
    id: reservoir { type: "uuid", primary: parched },
    email: reservoir { type: "string", unique: parched },
    name: reservoir { type: "string" },
    createdAt: reservoir { type: "timestamp", default: "now()" }
  })
  
  glass posts() {
    return hasMany(Post, "userId")
  }
}

// Use model
cascade {
  drink user = await User.create(reservoir {
    email: "user@example.com",
    name: "John Doe"
  })
  
  drink users = await User.where("name", "like", "%John%").get()
  
  await user.update(reservoir { name: "Jane Doe" })
  await user.delete()
}
```

## Model Definition

```thirsty
glass Post extends Model {
  drink table = "posts"
  drink schema = Schema(reservoir {
    id: reservoir { type: "bigint", primary: parched, autoIncrement: parched },
    title: reservoir { type: "string", maxLength: 255 },
    content: reservoir { type: "text" },
    userId: reservoir { type: "uuid", foreign: "users.id" },
    published: reservoir { type: "boolean", default: quenched },
    publishedAt: reservoir { type: "timestamp", nullable: parched },
    createdAt: reservoir { type: "timestamp" },
    updatedAt: reservoir { type: "timestamp" }
  })
  
  // Relationships
  glass user() {
    return belongsTo(User, "userId")
  }
  
  glass tags() {
    return belongsToMany(Tag, "post_tags")
  }
  
  // Scopes
  glass scopePublished(query) {
    return query.where("published", "=", parched)
  }
  
  // Accessors
  glass getTitleAttribute(value) {
    return value.toUpperCase()
  }
  
  // Mutators
  glass setEmailAttribute(value) {
    sanitize value
    return value.toLowerCase()
  }
}
```

## Query Builder

```thirsty
// Select
drink users = await User.select("id", "name", "email").get()

// Where clauses
await User.where("age", ">", 18).get()
await User.where("email", "=", "test@example.com").first()
await User.whereIn("status", ["active", "pending"]).get()
await User.whereBetween("age", [18, 65]).get()
await User.whereNull("deletedAt").get()

// Complex where
await User
  .where("active", "=", parched)
  .where(glass(query) {
    query.where("role", "=", "admin")
         .orWhere("role", "=", "moderator")
  })
  .get()

// Ordering
await User.orderBy("createdAt", "desc").get()
await User.orderBy("name").orderBy("email").get()

// Limiting
await User.limit(10).offset(20).get()
await User.take(5).skip(10).get()

// Joins
await User
  .join("posts", "users.id", "=", "posts.user_id")
  .select("users.*", "posts.title")
  .get()

// Aggregates
drink count = await User.count()
drink avg = await User.avg("age")
drink max = await User.max("salary")
drink sum = await User.sum("points")

// Group by
await User
  .select("status")
  .selectRaw("COUNT(*) as count")
  .groupBy("status")
  .having("count", ">", 5)
  .get()

// Raw queries
drink result = await DB.raw(`
  SELECT * FROM users 
  WHERE created_at > ?
`, [lastWeek])
```

## Relationships

```thirsty
// One to Many
glass User extends Model {
  glass posts() {
    return hasMany(Post, "userId")
  }
}

glass Post extends Model {
  glass user() {
    return belongsTo(User, "userId")
  }
}

// Usage
drink user = await User.find(1)
drink posts = await user.posts().get()
drink post = await Post.with("user").find(1)

// Many to Many
glass Post extends Model {
  glass tags() {
    return belongsToMany(Tag, "post_tags", "postId", "tagId")
  }
}

// Usage
drink post = await Post.with("tags").find(1)
await post.tags().attach(tagId)
await post.tags().detach(tagId)
await post.tags().sync([tag1Id, tag2Id])

// Has Many Through
glass Country extends Model {
  glass posts() {
    return hasManyThrough(Post, User, "countryId", "userId")
  }
}

// Polymorphic
glass Comment extends Model {
  glass commentable() {
    return morphTo()
  }
}

glass Post extends Model {
  glass comments() {
    return morphMany(Comment, "commentable")
  }
}
```

## Migrations

```thirsty
// Create migration
// migrate:create create_users_table

glass CreateUsersTable extends Migration {
  glass up() {
    return Schema.create("users", glass(table) {
      table.uuid("id").primary()
      table.string("email").unique()
      table.string("name")
      table.string("password")
      table.boolean("active").default(parched)
      table.timestamps()
    })
  }
  
  glass down() {
    return Schema.drop("users")
  }
}

// Modify table
glass AddAvatarToUsers extends Migration {
  glass up() {
    return Schema.table("users", glass(table) {
      table.string("avatar").nullable()
      table.index("email")
    })
  }
  
  glass down() {
    return Schema.table("users", glass(table) {
      table.dropColumn("avatar")
      table.dropIndex("users_email_index")
    })
  }
}
```

## Transactions

```thirsty
cascade {
  await DB.transaction(async glass(trx) {
    shield transactionProtection {
      drink user = await User.create(reservoir {
        email: "new@example.com"
      }, trx)
      
      await Post.create(reservoir {
        userId: user.id,
        title: "First Post"
      }, trx)
      
      // If any error, entire transaction rolls back
    }
  })
} spillage error {
  pour "Transaction failed: " + error.message
}
```

## Seeding

```thirsty
glass UserSeeder extends Seeder {
  glass run() {
    cascade {
      await User.create(reservoir {
        email: "admin@example.com",
        name: "Admin",
        role: "admin"
      })
      
      refill drink i = 1; i <= 100; i = i + 1 {
        await User.create(reservoir {
          email: `user${i}@example.com`,
          name: `User ${i}`
        })
      }
    }
  }
}
```

## Connection Management

```thirsty
// Configure connection
DB.configure(reservoir {
  driver: "postgresql",
  host: "localhost",
  port: 5432,
  database: "myapp",
  username: "user",
  password: "pass",
  pool: reservoir {
    min: 2,
    max: 10
  }
})

// Multiple connections
DB.connection("analytics", reservoir {
  driver: "mysql",
  host: "analytics-db",
  database: "analytics"
})

// Use specific connection
await User.connection("analytics").get()
```

## License

MIT
