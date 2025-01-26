# GAME SDK Examples

This directory contains examples demonstrating various aspects of the GAME SDK.

## Directory Structure

- `basic/`: Basic examples demonstrating core functionality
  - Weather agent examples
  - Basic agent and worker testing
  - Custom agent functionality

- `error_handling/`: Examples of proper error handling
  - General error handling patterns
  - Network error handling
  - Plugin error handling

- `testing/`: Examples of testing practices
  - Worker testing patterns
  - Test organization

- `advanced/`: Advanced usage examples
  - Complex agent interactions
  - Custom plugin development
  - Advanced state management

## Getting Started

1. First, set up your environment:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual API keys
   # NEVER commit your .env file to version control!
   ```

2. Required environment variables:
   - `VIRTUALS_API_KEY`: Your Virtuals API key (required)
   - `GAME_API_KEY`: Your GAME API key (required)
   
   Optional environment variables:
   - `DEFI_LAMA_API_KEY`: For DeFi features
   - `MESSARI_API_KEY`: For DeFi insights
   - `ENVIRONMENT`: Set to 'development' or 'production'
   - `DEBUG`: Set to 'True' or 'False'
   - `LOG_LEVEL`: Set to 'INFO', 'DEBUG', etc.

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Try running the weather example:
   ```bash
   python basic/example_weather_agent.py
   ```

## Example Types

### Hosted Agents (Recommended)
The `hosted_agent` directory contains examples using the hosted agent approach. This is the recommended way to use the SDK because:
- Simpler implementation
- Managed infrastructure
- Built-in scaling and monitoring
- Easier deployment

### Core SDK
The `game` directory contains examples using the core SDK. These are primarily used for:
- Testing core functionality
- Understanding the SDK internals
- Building custom integrations

## Security Notes
- Never commit API keys or sensitive information to version control
- Always use environment variables for sensitive values
- The `.env` file is ignored by git to prevent accidental commits
- Use `.env.example` as a template, but never put real values in it

## Contributing
When adding new examples:
1. Use the hosted agent approach unless you have a specific reason not to
2. Follow the existing code structure and style
3. Include proper error handling and logging
4. Add documentation and usage examples
5. Update this README with your new example
6. Never commit sensitive information or API keys
