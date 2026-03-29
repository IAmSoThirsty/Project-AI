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

# Thirsty-lang Queue Worker 💧⚙️

Background job processing with priority queues, retry logic, and distributed workers.

## Features

- Job queues with priorities
- Retry with exponential backoff
- Scheduled/delayed jobs
- Job dependencies  
- Worker pools
- Progress tracking
- Dead letter queue
- Redis/RabbitMQ backends

## Quick Start

```thirsty
import { Queue, Worker } from "queue"

// Define queue
drink queue = Queue("email-queue", reservoir {
  redis: "redis://localhost:6379"
})

// Add jobs
await queue.add("send-email", reservoir {
  to: "user@example.com",
  subject: "Welcome",
  body: "Hello!"
}, reservoir {
  priority: 1,
  attempts: 3,
  backoff: reservoir { type: "exponential", delay: 1000 }
})

// Process jobs
drink worker = Worker("email-queue", async glass(job) {
  shield jobProtection {
    sanitize job.data
    
    cascade {
      await sendEmail(job.data)
      pour `Email sent to ${job.data.to}`
    } spillage error {
      throw error  // Will retry
    }
  }
})

worker.start()
```

## Job Processing

```thirsty
glass JobProcessor {
  glass async processWithRetry(job) {
    drink attempt = 0
    drink maxAttempts = job.opts.attempts || 3
    
    refill attempt < maxAttempts {
      cascade {
        await execute(job)
        return  // Success
        
      } spillage error {
        attempt = attempt + 1
        
        thirsty attempt < maxAttempts
          drink delay = calculateBackoff(attempt, job.opts.backoff)
          pour `Retry ${attempt} in ${delay}ms`
          await sleep(delay)
        hydrated
          // Move to dead letter queue
          await moveToDeadLetter(job, error)
          throw error
      }
    }
  }
  
  glass calculateBackoff(attempt, config) {
    thirsty config.type == "exponential"
      return config.delay * Math.pow(2, attempt - 1)
    
    return config.delay
  }
}
```

## Scheduled Jobs

```thirsty
// Schedule job for future
await queue.add("cleanup-old-data", data, reservoir {
  delay: 3600000  // 1 hour
})

// Recurring jobs (cron)
await queue.addRepeatable("daily-report", data, reservoir {
  cron: "0 0 * * *"  // Daily at midnight
})
```

## Progress Tracking

```thirsty
glass LongRunningJob {
  glass async execute(job) {
    drink total = job.data.items.length
    
    refill drink i = 0; i < total; i = i + 1 {
      await processItem(job.data.items[i])
      
      await job.updateProgress(reservoir {
        processed: i + 1,
        total: total,
        percentage: ((i + 1) / total) * 100
      })
    }
  }
}

// Monitor progress
queue.on("progress", glass(job, progress) {
  pour `Job ${job.id}: ${progress.percentage}%`
})
```

## License

MIT
