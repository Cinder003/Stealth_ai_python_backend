# 📱 Viewing Generated LLM Code in Docker Logs

This guide shows you how to view the generated LLM code and processing details in the Docker container logs.

## 🎯 What You'll See in the Logs

The enhanced logging now shows:

### 1. **Processing Overview**
```
🚀 STARTING FIGMA FRAME PROCESSING
============================================================
🎯 Processing Figma file: oqat2jknkfaeKkebJpNbeL
📋 Target frames: All frames
🎨 Framework: react
⚙️  Backend: nodejs
💬 User message: Generate a modern web application
============================================================
```

### 2. **Frame-by-Frame Processing**
```
🎯 Processing frame 1/5: 1:2
⏱️  Progress: 20.0%
📡 Fetching frame data using get_nodes() API...
✅ Frame data received: 15420 characters
🧠 Processing with LLM...
🤖 Sending prompt to LLM for frame: HomePage
📏 Prompt length: 15420 characters
```

### 3. **Raw LLM Response** (This is what you want to see!)
```
🎯 LLM Response for frame 'HomePage' (1:2):
================================================================================
{
  "frontend": {
    "src/components/HomePage.tsx": "import React from 'react';\n\ninterface HomePageProps {\n  className?: string;\n}\n\nexport const HomePage: React.FC<HomePageProps> = ({ className = '' }) => {\n  return (\n    <div className={`min-h-screen bg-gray-50 ${className}`}>\n      <header className=\"bg-white shadow-sm\">\n        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">\n          <div className=\"flex justify-between items-center py-6\">\n            <h1 className=\"text-3xl font-bold text-gray-900\">NGO Platform</h1>\n            <nav className=\"hidden md:flex space-x-8\">\n              <a href=\"#\" className=\"text-gray-500 hover:text-gray-900\">Home</a>\n              <a href=\"#\" className=\"text-gray-500 hover:text-gray-900\">About</a>\n              <a href=\"#\" className=\"text-gray-500 hover:text-gray-900\">Contact</a>\n            </nav>\n          </div>\n        </div>\n      </header>\n      <main className=\"max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8\">\n        <div className=\"text-center\">\n          <h2 className=\"text-4xl font-extrabold text-gray-900 sm:text-5xl\">\n            Welcome to Our NGO\n          </h2>\n          <p className=\"mt-4 text-xl text-gray-600\">\n            Making a difference in the world, one step at a time.\n          </p>\n        </div>\n      </main>\n    </div>\n  );\n};\n"
  },
  "backend": {
    "src/api/home.ts": "import { Request, Response } from 'express';\n\n/**\n * GET /api/home\n * Get homepage data\n */\nexport const getHomeData = async (req: Request, res: Response) => {\n  try {\n    const homeData = {\n      title: 'NGO Platform',\n      description: 'Making a difference in the world',\n      stats: {\n        projects: 150,\n        volunteers: 2500,\n        donations: 50000\n      }\n    };\n\n    res.json(homeData);\n  } catch (error) {\n    res.status(500).json({ error: 'Internal server error' });\n  }\n};\n"
  },
  "registryEntry": {
    "componentName": "HomePage",
    "path": "src/components/HomePage.tsx",
    "variants": ["desktop", "mobile"],
    "tokens": ["--color-gray-50", "--color-gray-900", "--shadow-sm"],
    "screensUsed": ["HomePage"],
    "dependencies": [],
    "apiEndpoints": ["/api/home"],
    "lastGenerated": "2025-01-25T12:00:00Z"
  }
}
================================================================================
📊 Response length: 2847 characters
```

### 4. **Code Parsing Details**
```
🔍 Parsing generated code...
   📏 Code length: 2847 characters
   🔤 Starts with: {
   📋 Detected JSON format, parsing...
   ✅ JSON parsing successful!
   📁 Frontend files: 1
   📁 Backend files: 1
```

### 5. **File Processing Results**
```
📁 Parsed files for frame 'HomePage':
   Frontend files: 1
   Backend files: 1
   📄 Frontend: src/components/HomePage.tsx
   📄 Backend: src/api/home.ts
```

### 6. **Final Summary**
```
🎉 PROCESSING COMPLETE!
============================================================
📊 Summary:
   ✅ Successful frames: 5/5
   ⏱️  Total processing time: 45.23s
   🔢 Total tokens used: 12,450
   📁 Total files generated: 15
   🎯 Average time per frame: 9.05s
   🚀 Tokens per second: 275
============================================================
```

## 🛠️ How to View the Logs

### Method 1: Real-time Logs (Recommended)
```bash
# View app container logs in real-time
docker-compose logs -f app

# View all container logs
docker-compose logs -f

# View worker container logs (if processing is done there)
docker-compose logs -f worker
```

### Method 2: Recent Logs
```bash
# View last 100 lines
docker-compose logs --tail=100 app

# View last 500 lines
docker-compose logs --tail=500 app
```

### Method 3: Using the Helper Script
```bash
python examples/view_docker_logs.py
```

### Method 4: Save Logs to File
```bash
# Save logs to file for analysis
docker-compose logs app > figma_processing_logs.txt
```

## 🔍 What to Look For

### ✅ **Successful Processing**
- Look for `🎯 LLM Response for frame` sections
- Check for `✅ JSON parsing successful!` or `✅ Text parsing complete!`
- Verify file counts: `📁 Frontend files: X`, `📁 Backend files: Y`

### ❌ **Parsing Issues**
- Look for `❌ Error parsing generated code`
- Check if LLM response format is unexpected
- Verify if JSON parsing fails and falls back to text parsing

### 🐛 **Debugging Tips**
1. **If no LLM response appears**: Check if the LLM service is running
2. **If parsing fails**: Look at the raw response format to improve parsing logic
3. **If files aren't saved**: Check the file saving section in the logs

## 📊 Performance Metrics

The logs now show detailed performance metrics:
- **Processing time per frame**
- **Total tokens used**
- **Files generated**
- **Success rate**
- **Tokens per second**

## 🎯 Key Benefits

1. **🔍 Full Visibility**: See exactly what the LLM generates
2. **🐛 Easy Debugging**: Identify parsing issues quickly
3. **📊 Performance Tracking**: Monitor processing speed and efficiency
4. **💡 Improvement Insights**: See where to enhance parsing logic

## 🚀 Next Steps

Based on the logs, you can:
1. **Improve parsing logic** if you see consistent parsing failures
2. **Optimize prompts** if LLM responses aren't in the expected format
3. **Enhance file saving** if generated files aren't being saved correctly
4. **Monitor performance** to identify bottlenecks

The enhanced logging gives you complete visibility into the Figma processing pipeline!
