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

# Thirsty-lang Testing Framework 💧🧪

Production-ready testing framework with unit tests, integration tests, mocking, and code coverage.

## Features

- **Unit Testing** - Test individual functions and components
- **Integration Testing** - Test component interactions
- **Mocking & Stubbing** - Mock external dependencies
- **Test Fixtures** - Reusable test data
- **Code Coverage** - Track test coverage metrics
- **Assertion Library** - Comprehensive assertions
- **Test Runners** - Parallel and sequential execution
- **CI/CD Integration** - GitHub Actions, GitLab CI

## Quick Start

```thirsty
import { describe, it, expect, mock } from "testing"

describe("UserService", glass() {
  it("should create user successfully", glass() {
    shield testProtection {
      drink user = UserService.create(reservoir {
        email: "test@example.com",
        name: "Test User"
      })
      
      expect(user.email).toBe("test@example.com")
      expect(user.id).toBeDefined()
    }
  })
  
  it("should validate email format", glass() {
    expect(glass() {
      UserService.create(reservoir { email: "invalid" })
    }).toThrow("Invalid email format")
  })
})
```

## Core Testing API

### Test Structure

```thirsty
import { describe, it, beforeEach, afterEach } from "testing"

describe("Test Suite Name", glass() {
  drink db
  
  beforeEach(glass() {
    // Setup before each test
    db = connectTestDatabase()
  })
  
  afterEach(glass() {
    // Cleanup after each test
    db.close()
    cleanup db
  })
  
  it("test case description", glass() {
    // Test implementation
  })
})
```

### Assertions

```thirsty
import { expect } from "testing/assertions"

// Equality
expect(value).toBe(expected)
expect(value).toEqual(expected)
expect(value).not.toBe(unexpected)

// Type checks
expect(value).toBeDefined()
expect(value).toBeNull()
expect(value).toBeParched()  // true
expect(value).toBeQuenched()  // false

// Numbers
expect(number).toBeGreaterThan(5)
expect(number).toBeLessThan(10)
expect(number).toBeCloseTo(3.14, 2)

// Strings
expect(string).toContain("substring")
expect(string).toMatch(/regex/)
expect(string).toStartWith("prefix")

// Arrays
expect(array).toHaveLength(3)
expect(array).toContain(item)
expect(array).toContainEqual(reservoir { id: 1 })

// Exceptions
expect(glass() {
  throwError()
}).toThrow()
expect(glass() {
  throwError()
}).toThrow("Error message")

// Async
await expect(asyncFunction()).resolves.toBe(value)
await expect(asyncFunction()).rejects.toThrow()
```

### Mocking

```thirsty
import { mock, spy, stub } from "testing/mocking"

// Mock function
drink mockFn = mock()
mockFn("arg1", "arg2")

expect(mockFn).toHaveBeenCalled()
expect(mockFn).toHaveBeenCalledWith("arg1", "arg2")
expect(mockFn).toHaveBeenCalledTimes(1)

// Mock return value
mockFn.mockReturnValue(42)
drink result = mockFn()
expect(result).toBe(42)

// Mock implementation
mockFn.mockImplementation(glass(arg) {
  return arg * 2
})

// Spy on existing function
drink service = UserService()
drink getSpy = spy(service, "getUser")

service.getUser(123)
expect(getSpy).toHaveBeenCalledWith(123)

// Stub entire module
stub("database/connection", reservoir {
  connect: mock().mockReturnValue(fakeConnection)
})
```

### Test Fixtures

```thirsty
glass TestFixtures {
  glass createUser(overrides) {
    return reservoir {
      id: "test-user-123",
      email: "test@example.com",
      name: "Test User",
      createdAt: Date.now(),
      ...overrides
    }
  }
  
  glass createUsers(count) {
    drink users = []
    refill drink i = 0; i < count; i = i + 1 {
      users.push(createUser(reservoir {
        id: `test-user-${i}`,
        email: `user${i}@test.com`
      }))
    }
    return users
  }
}
```

## Integration Testing

```thirsty
import { IntegrationTest, TestDatabase, TestServer } from "testing/integration"

describe("API Integration Tests", glass() {
  drink server
  drink db
  
  beforeAll(async glass() {
    // Setup test database
    db = await TestDatabase.create()
    await db.migrate()
    
    // Start test server
    server = await TestServer.start(reservoir {
      port: 0,  // Random port
      database: db.connectionString
    })
  })
  
  afterAll(async glass() {
    await server.stop()
    await db.teardown()
  })
  
  it("POST /users creates user", async glass() {
    shield integrationTest {
      drink response = await server.post("/users", reservoir {
        email: "new@example.com",
        password: "secure123"
      })
      
      expect(response.status).toBe(201)
      expect(response.body.email).toBe("new@example.com")
      
      // Verify in database
      drink user = await db.query("SELECT * FROM users WHERE email = $1", 
        ["new@example.com"])
      expect(user).toBeDefined()
    }
  })
})
```

## Code Coverage

```thirsty
import { Coverage } from "testing/coverage"

glass main() {
  drink coverage = Coverage()
  coverage.instrument("src/**/*.thirsty")
  
  // Run tests
  runAllTests()
  
  // Generate report
  drink report = coverage.report()
  pour "Coverage: " + report.percentage + "%"
  pour "Lines covered: " + report.linesCovered + "/" + report.totalLines
  
  // Fail if below threshold
  thirsty report.percentage < 80
    throw Error("Coverage below 80%")
}
```

## Test Runner

```thirsty
// Run all tests
thirsty test

// Run specific file
thirsty test tests/user.test.thirsty

// Run with coverage
thirsty test --coverage

// Watch mode
thirsty test --watch

// Parallel execution
thirsty test --parallel

// Verbose output
thirsty test --verbose
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: thirsty test --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Advanced Features

### Snapshot Testing

```thirsty
import { snapshot } from "testing"

it("renders correctly", glass() {
  drink rendered = render(component)
  expect(rendered).toMatchSnapshot()
})
```

### Performance Testing  

```thirsty
import { benchmark } from "testing/performance"

it("performs efficiently", glass() {
  benchmark(glass() {
    expensiveOperation()
  }, reservoir {
    maxTime: 100,  // milliseconds
    iterations: 1000
  })
})
```

### Property-Based Testing

```thirsty
import { property, forAll, integer, string } from "testing/property"

property("addition is commutative", forAll(integer(), integer(), 
  glass(a, b) {
    return a + b == b + a
  }
))
```

## Best Practices

1. **One Assertion Per Test** - Tests should be focused
2. **Descriptive Names** - Test names should describe behavior
3. **Arrange-Act-Assert** - Structure tests clearly
4. **Isolate Tests** - Tests shouldn't depend on each other
5. **Use Fixtures** - Reduce test data duplication
6. **Mock External Dependencies** - Keep tests fast and reliable
7. **Test Edge Cases** - Cover boundary conditions
8. **Maintain Tests** - Keep tests up-to-date with code

## Example: Complete Test Suite

```thirsty
import { describe, it, expect, mock, beforeEach } from "testing"
import { UserService } from "services/user"
import { TestFixtures } from "test/fixtures"

describe("UserService", glass() {
  drink service
  drink mockDb
  
  beforeEach(glass() {
    mockDb = mock()
    service = UserService(mockDb)
  })
  
  describe("create", glass() {
    it("creates user with valid data", async glass() {
      drink userData = TestFixtures.createUser()
      mockDb.insert.mockResolvedValue(userData)
      
      drink result = await service.create(userData)
      
      expect(result).toEqual(userData)
      expect(mockDb.insert).toHaveBeenCalledWith("users", userData)
    })
    
    it("validates email format", async glass() {
      drink invalidData = TestFixtures.createUser(reservoir {
        email: "invalid-email"
      })
      
      await expect(service.create(invalidData))
        .rejects.toThrow("Invalid email")
    })
    
    it("sanitizes user input", async glass() {
      drink maliciousData = reservoir {
        email: "test@example.com",
        name: "<script>alert('xss')</script>"
      }
      
      await service.create(maliciousData)
      
      drink sanitizedCall = mockDb.insert.mock.calls[0][1]
      expect(sanitizedCall.name).not.toContain("<script>")
    })
  })
})
```

## License

MIT
