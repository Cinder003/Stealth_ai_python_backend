# Testing Large Figma Files with Postman

## 🚀 Quick Setup for Your 44k Node File

### Your Figma File Details
- **URL**: https://www.figma.com/proto/oqat2jknkfaeKkebJpNbeL/NGO-PROJECT
- **File Key**: `oqat2jknkfaeKkebJpNbeL`
- **Expected Issue**: "Too many nodes: 44656"

---

## 📋 Postman Collection Setup

### 1. **Analyze File Endpoint**
```
POST http://localhost:8000/api/v1/figma/analyze
Content-Type: application/json

{
  "file_id": "oqat2jknkfaeKkebJpNbeL",
  "access_token": "YOUR_FIGMA_ACCESS_TOKEN"
}
```

**Expected Response (Success):**
```json
{
  "success": true,
  "analysis": {
    "processing_mode": "screen_by_screen",
    "screens": {
      "Screen 1": { "node_count": 15000, "can_process": true },
      "Screen 2": { "node_count": 12000, "can_process": true },
      "Screen 3": { "node_count": 17656, "can_process": true }
    },
    "shared_components": [...],
    "navigation": {...}
  }
}
```

### 2. **Generate Code Endpoint**
```
POST http://localhost:8000/api/v1/figma/generate
Content-Type: application/json

{
  "file_id": "oqat2jknkfaeKkebJpNbeL",
  "framework": "react",
  "backend_framework": "nodejs",
  "include_assets": true,
  "user_message": "Generate complete NGO project application"
}
```

**Expected Response (Success):**
```json
{
  "success": true,
  "generated_code": {
    "screens": {
      "Screen 1": {
        "frontend_code": {...},
        "backend_code": {...}
      }
    },
    "shared_components": {...},
    "navigation": {...}
  },
  "metadata": {
    "processing_mode": "screen_by_screen",
    "total_screens": 3,
    "shared_components_count": 15
  }
}
```

---

## 🔧 cURL Commands

### Test File Analysis
```bash
curl -X POST http://localhost:8000/api/v1/figma/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "oqat2jknkfaeKkebJpNbeL",
    "access_token": "YOUR_FIGMA_ACCESS_TOKEN"
  }'
```

### Test Code Generation
```bash
curl -X POST http://localhost:8000/api/v1/figma/generate \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "oqat2jknkfaeKkebJpNbeL",
    "framework": "react",
    "backend_framework": "nodejs",
    "include_assets": true,
    "user_message": "Generate complete NGO project"
  }'
```

---

## ✅ What to Look For

### Before Our Fix (Old Behavior)
```json
{
  "success": false,
  "error": "Figma processing failed: Invalid Figma JSON: Too many nodes: 44656"
}
```

### After Our Fix (New Behavior)
```json
{
  "success": true,
  "analysis": {
    "processing_mode": "screen_by_screen",
    "screens": {...},
    "shared_components": [...],
    "navigation": {...}
  }
}
```

---

## 🎯 Key Success Indicators

1. **No "Too many nodes" error** ✅
2. **`processing_mode: "screen_by_screen"`** ✅
3. **Multiple screens detected** ✅
4. **Shared components extracted** ✅
5. **Navigation structure generated** ✅

---

## 🔑 Getting Your Figma Access Token

1. Go to https://www.figma.com/developers/api#authentication
2. Click "Get personal access token"
3. Generate a new token
4. Copy and use in your requests

---

## 🚀 Quick Test Steps

1. **Start the API server**: `docker-compose up -d`
2. **Get your Figma token** from the link above
3. **Open Postman** and create the requests above
4. **Test the analyze endpoint** first
5. **Test the generate endpoint** if analysis succeeds
6. **Verify** you get screen-by-screen processing instead of the node limit error

---

## 📊 Expected Results

- **Original**: 44,656 nodes → "Too many nodes" error
- **New**: 44,656 nodes → Split into 3 screens of ~15k nodes each
- **Result**: Successful processing with complete code generation
