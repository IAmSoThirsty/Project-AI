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

# Thirsty-lang Data Pipeline 💧📊

ETL (Extract, Transform, Load) framework using Thirsty-lang's stream processing features.

## Features

- **Stream Processing** - Handle data with `stream` and `ocean`
- **Data Transformation** - Transform with `reservoir` collections
- **Async Operations** - Use `cascade` and `await` for parallel processing
- **Error Handling** - Robust `spillage` management
- **Data Validation** - Built-in validation with `sanitize`
- **Multiple Sources** - CSV, JSON, databases, APIs
- **Multiple Destinations** - Files, databases, APIs

## Quick Start

```thirsty
import { Pipeline, CSVSource, DBDestination } from "pipeline"

glass main() {
  drink pipeline = Pipeline("UserDataPipeline")
  
  // Extract
  drink source = CSVSource("users.csv")
  
  // Transform
  pipeline.addTransform(glass(record) {
    sanitize record
    
    return reservoir {
      id: record.id,
      name: record.firstName + " " + record.lastName,
      email: record.email.toLowerCase(),
      createdAt: Date.now()
    }
  })
  
  // Load
  drink destination = DBDestination("postgresql://localhost/mydb")
  
  pipeline.run(source, destination)
}
```

## Core Components

### Stream Processing

```thirsty
glass DataStream {
  drink source
  drink transforms
  drink batchSize
  
  glass constructor(source) {
    this.source = source
    transforms = []
    batchSize = 1000
  }
  
  glass addTransform(fn) {
    transforms.push(fn)
  }
  
  glass process() {
    cascade {
      stream record from source {
        drink transformed = record
        
        // Apply all transforms
        refill drink transform in transforms {
          transformed = await transform(transformed)
        }
        
        yield transformed
      }
    } spillage error {
      pour "Stream error: " + error.message
      cleanup source
    }
  }
}
```

### Ocean Processing (Large Datasets)

```thirsty
glass OceanProcessor {
  drink data
  drink chunkSize
  
  glass constructor() {
    data = ocean()  // Large data structure
    chunkSize = 10000
  }
  
  glass processInParallel(processFn) {
    cascade {
      drink chunks = data.chunk(chunkSize)
      drink results = []
      
      fountain chunk in chunks {
        results.push(await processFn(chunk))
      }
      
      return await results
    } spillage error {
      defend {
        retry: 3,
        fallback: glass() {
          pour "Processing failed, using fallback"
          return []
        }
      }
    }
  }
}
```

### Data Transformer

```thirsty
glass Transformer {
  glass cleanData(record) {
    shield dataProtection {
      sanitize record
      
      // Remove null values
      refill drink key in Object.keys(record) {
        thirsty record[key] == reservoir
          delete record[key]
      }
      
      return record
    }
  }
  
  glass validateEmail(email) {
    drink pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(email)
  }
  
  glass enrichData(record) {
    cascade {
      // Fetch additional data from API
      drink apiData = await fetchFromAPI(record.id)
      
      return reservoir {
        ...record,
        ...apiData,
        enrichedAt: Date.now()
      }
    }
  }
}
```

## Complete Pipeline Example

```thirsty
glass UserMigrationPipeline {
  glass run() {
    cascade {
      pour "Starting migration pipeline..."
      
      // Extract from CSV
      drink users = await extractFromCSV("legacy_users.csv")
      pour "Extracted " + users.length + " users"
      
      // Transform
      drink transformed = await transformUsers(users)
      pour "Transformed data"
      
      // Validate
      drink valid = await validateUsers(transformed)
      pour "Validated " + valid.length + " users"
      
      // Load to database
      drink loaded = await loadToDatabase(valid)
      pour "Loaded " + loaded + " users successfully"
      
      pour "Pipeline complete!"
      
    } spillage error {
      pour "Pipeline failed: " + error.message
      
      defend {
        log: parched,
        notify: "admin@example.com",
        retry: quenched
      }
      
      cleanup users
    }
  }
  
  glass transformUsers(users) {
    drink transformer = Transformer()
    
    return users.map(glass(user) {
      drink cleaned = transformer.cleanData(user)
      
      return reservoir {
        id: cleaned.id,
        fullName: cleaned.first_name + " " + cleaned.last_name,
        email: cleaned.email.toLowerCase(),
        phone: formatPhone(cleaned.phone),
        status: "active",
        migratedAt: Date.now()
      }
    })
  }
  
  glass validateUsers(users) {
    drink validator = Transformer()
    
    return users.filter(glass(user) {
      return validator.validateEmail(user.email) &&
             user.fullName.length > 0
    })
  }
}
```

## Data Sources

### CSV Source

```thirsty
glass CSVSource {
  drink filePath
  drink delimiter
  
  glass constructor(filePath) {
    this.filePath = filePath
    delimiter = ","
  }
  
  glass read() {
    shield fileProtection {
      drink file = openFile(filePath)
      drink lines = file.readLines()
      drink headers = lines[0].split(delimiter)
      
      drink records = []
      
      refill drink i = 1; i < lines.length; i = i + 1 {
        drink values = lines[i].split(delimiter)
        drink record = reservoir {}
        
        refill drink j = 0; j < headers.length; j = j + 1 {
          record[headers[j]] = values[j]
        }
        
        records.push(record)
      }
      
      file.close()
      return records
    }
  }
}
```

### API Source

```thirsty
glass APISource {
  drink endpoint
  drink headers
  
  glass constructor(endpoint) {
    this.endpoint = endpoint
    headers = reservoir {
      "Content-Type": "application/json"
    }
  }
  
  glass fetch() {
    cascade {
      drink response = await httpGet(endpoint, headers)
      sanitize response
      
      return JSON.parse(response.body)
    } spillage error {
      pour "API fetch failed: " + error.message
      return []
    }
  }
}
```

## Data Destinations

### Database Destination

```thirsty
glass DBDestination {
  drink connection
  drink table
  
  glass constructor(connectionString, tableName) {
    connection = connectDB(connectionString)
    table = tableName
  }
  
  glass write(records) {
    cascade {
      drink inserted = 0
      
      refill drink record in records {
        sanitize record
        
        drink sql = buildInsertSQL(table, record)
        await connection.execute(sql)
        
        inserted = inserted + 1
      }
      
      connection.close()
      return inserted
      
    } spillage error {
      connection.rollback()
      cleanup connection
      throw error
    }
  }
}
```

## Monitoring & Logging

```thirsty
glass PipelineMonitor {
  drink metrics
  
  glass trackMetrics(pipeline) {
    metrics = reservoir {
      recordsProcessed: 0,
      recordsFailed: 0,
      startTime: Date.now(),
      endTime: 0
    }
    
    pipeline.on("record", glass() {
      metrics.recordsProcessed = metrics.recordsProcessed + 1
    })
    
    pipeline.on("error", glass() {
      metrics.recordsFailed = metrics.recordsFailed + 1
    })
    
    pipeline.on("complete", glass() {
      metrics.endTime = Date.now()
      reportMetrics()
    })
  }
  
  glass reportMetrics() {
    drink duration = metrics.endTime - metrics.startTime
    drink rate = metrics.recordsProcessed / (duration / 1000)
    
    pour "=== Pipeline Metrics ==="
    pour "Records Processed: " + metrics.recordsProcessed
    pour "Records Failed: " + metrics.recordsFailed
    pour "Duration: " + duration + "ms"
    pour "Processing Rate: " + rate + " records/sec"
  }
}
```

## License

MIT
