# Royal Guard Activity API & Roblox Integration

## API Deployment (Railway)

### Files:
- `activity_api.py` - Flask API with MongoDB integration
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment config
- `railway.json` - Railway service configuration
- `.env.example` - Environment variables template

### Endpoints:
- `GET /` - Health check
- `POST /update_activity` - Update player activity

### Deployment Steps:
1. Connect GitHub repo to Railway
2. Set root directory to `/API/`
3. Add `MONGO_URI` environment variable
4. Deploy automatically

## Roblox Integration

### Setup:
1. Place `RobloxActivityTracker.lua` in ServerScriptService
2. Update `API_URL` with your Railway deployment URL
3. Enable HTTP requests in game settings
4. Set `DEBUG_MODE = false` for production

### Features:
- Tracks player movement, jumping, and state changes
- Sends activity data every 60 seconds
- Handles player join/leave events
- Automatic cleanup and error handling

### Configuration:
```lua
local API_URL = "https://your-app-name.railway.app/update_activity"
local ACTIVITY_INTERVAL = 60 -- seconds
local DEBUG_MODE = false -- production setting
```
