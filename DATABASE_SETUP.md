# Database Setup Guide

## Automatic Database Initialization

The PostgreSQL database will automatically load your `full_dump.sql` file when the container starts for the first time. Here's how it works:

### 1. SQL File Location
Your SQL dump file is located at:
```
cs-chatbot/server/database/full_dump.sql
```

### 2. Docker Configuration
The docker-compose.yaml file automatically mounts this SQL file to the PostgreSQL container:
```yaml
volumes:
  - ./cs-chatbot/server/database/full_dump.sql:/docker-entrypoint-initdb.d/01-init.sql
```

### 3. What Happens on Startup
1. PostgreSQL container starts
2. If the database is empty (first time), it runs all `.sql` files in `/docker-entrypoint-initdb.d/`
3. Your `full_dump.sql` file is executed, creating all tables and inserting data
4. The database initialization check service verifies the data was loaded correctly
5. The main application starts

### 4. Database Schema
Your database includes these tables:
- `chat_history` - Stores chat conversations
- `garansi` - Warranty information
- `product` - Camera products catalog
- `users` - User information and order status

### 5. Environment Variables
Make sure to set these in your `.env` file:
```env
DB_NAME=chatbot
DB_USER=myuser
DB_PASSWORD=mypassword
```

### 6. Running the Application
```bash
# Start all services
docker-compose up --build

# Check database logs
docker-compose logs postgres

# Check if data was loaded
docker-compose exec postgres psql -U myuser -d chatbot -c "SELECT COUNT(*) FROM product;"
```

### 7. Troubleshooting
- If the database doesn't initialize properly, check the PostgreSQL logs
- Make sure the SQL file path is correct in docker-compose.yaml
- Verify the SQL file syntax is valid PostgreSQL
- Check that the database user has proper permissions

### 8. Data Persistence
Your data is stored in a Docker volume called `postgres_data`, so it persists between container restarts. To reset the database:
```bash
docker-compose down -v  # This will delete all data
docker-compose up --build  # This will reload the SQL file
```
