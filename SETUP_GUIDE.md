# AI-Enhanced GIS Ticket Management Setup Guide

## 🚀 Overview

Your GIS Ticket Management AI Agent now supports:
1. **OpenAI GPT Integration** - Automated AI responses
2. **Prompt Export System** - Manual AI model usage
3. **Hybrid Approach** - Fallback to rule-based responses

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file in your project root:

```env
# OpenAI Configuration (Required for AI features)
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# AI Agent Configuration
AI_ENABLED=true              # Set to false to disable AI
FALLBACK_TO_RULES=true       # Fallback to rules if AI fails
EXPORT_PROMPTS=true          # Export prompts for manual use

# App Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### 3. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up/login to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### 4. Run the Application

```bash
python src/app.py
```

## 🤖 AI Features

### Automated AI Analysis
- **Real-time ticket analysis** using OpenAI GPT models
- **Intelligent categorization** based on GIS domain knowledge
- **Smart priority assignment** considering urgency indicators
- **Professional response generation** with technical accuracy

### Manual AI Prompt Export
- **JSON prompt files** saved to `prompts_export/` directory
- **Copy-paste ready** for any AI model (ChatGPT, Claude, Gemini, etc.)
- **Complete context** including system and user prompts
- **Usage instructions** included in each export

## 📁 Exported Prompt Structure

Each exported prompt includes:

```json
{
  "metadata": {
    "ticket_id": "31149",
    "timestamp": "20250711_143022",
    "analysis_type": "full"
  },
  "system_prompt": "You are an expert GIS Technical Support AI...",
  "user_prompt": "Analyze this GIS support ticket...",
  "ticket_data": { /* Original ticket data */ },
  "suggested_models": ["gpt-4o", "claude-3.5-sonnet", "gemini-pro"],
  "usage_instructions": { /* Step by step guide */ }
}
```

## 🔧 Configuration Options

### AI Models Supported
- **gpt-4o** (Recommended for complex analysis)
- **gpt-4o-mini** (Faster, cost-effective)
- **gpt-3.5-turbo** (Budget option)

### Operating Modes

1. **Full AI Mode** (`AI_ENABLED=true`)
   - Uses OpenAI for all analysis
   - Exports prompts for manual use
   - Falls back to rules if API fails

2. **Rules + Export Mode** (`AI_ENABLED=false`, `EXPORT_PROMPTS=true`)
   - Uses rule-based analysis
   - Still exports prompts for manual AI use
   - No API costs

3. **Rules Only Mode** (`AI_ENABLED=false`, `EXPORT_PROMPTS=false`)
   - Traditional rule-based operation
   - No AI integration

## 💡 Usage Workflow

### For Automated Processing:
1. Upload XML ticket file
2. Click "Import XML Tickets"
3. Review categorization and analysis
4. Click "Begin AI Processing" for enhanced responses

### For Manual AI Processing:
1. Process tickets (exports prompts automatically)
2. Go to "AI Prompt Exports" section
3. Click "View Exported Prompts"
4. Select a prompt file
5. Copy system/user prompts to your preferred AI model
6. Get AI response and apply manually

## 🛠️ Troubleshooting

### Common Issues:

1. **OpenAI API Errors**
   - Check API key validity
   - Verify account has credits
   - Check rate limits

2. **No Prompts Exported**
   - Ensure `EXPORT_PROMPTS=true`
   - Check `prompts_export/` directory permissions

3. **Import Errors**
   - Verify XML file format
   - Check file size limits

### Error Messages:
- `⚠️ OpenAI API key not configured` - Add valid API key to `.env`
- `⚠️ Failed to parse AI response` - Model returned invalid JSON
- `⚠️ OpenAI API error` - Check API key and credits

## 💰 Cost Considerations

### OpenAI API Costs (Approximate):
- **gpt-4o-mini**: ~$0.0001 per ticket
- **gpt-4o**: ~$0.001 per ticket

### Cost Optimization:
- Use `gpt-4o-mini` for most tickets
- Enable `FALLBACK_TO_RULES=true`
- Export prompts for manual processing of complex tickets

## 🔐 Security Notes

- Keep your `.env` file secure and never commit it to version control
- Your OpenAI API key has access to your account
- Ticket data is sent to OpenAI when AI_ENABLED=true
- Exported prompts contain ticket content for manual processing

## 📈 Performance Tips

1. **Batch Processing**: Process multiple tickets together
2. **Model Selection**: Use gpt-4o-mini for routine tickets
3. **Caching**: Results are cached locally for repeat analysis
4. **Monitoring**: Check the statistics dashboard for performance metrics

## 🎯 Next Steps

1. Test with sample tickets
2. Configure your preferred AI model
3. Set up monitoring and logging
4. Train your team on the new workflow
5. Consider integrating with your existing ticket system

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify configuration settings
4. Test with simple ticket examples
