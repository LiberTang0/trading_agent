# Trading Agent Testing Guide

This guide explains how to run tests for your trading agent to ensure everything works correctly before running it 24/7.

## 🧪 Test Structure

### Test Files
- `test_trading_agent.py` - Comprehensive unit tests for all components
- `test_market_hours.py` - Specific tests for market hours and forex trading
- `test_stream.py` - Streaming connection tests
- `test_stream_simple.py` - Simple streaming compatibility tests
- `run_tests.py` - Test runner with different categories
- `pytest.ini` - Pytest configuration

### Test Categories

#### 1. **Quick Tests** (Fastest)
```bash
python run_tests.py --category quick
```
- ✅ Import checks
- ✅ Data structure validation
- ✅ Model file existence
- ⏱️ Runs in ~2 seconds

#### 2. **Integration Tests** (Medium)
```bash
python run_tests.py --category integration
```
- ✅ API configuration
- ✅ Streaming library imports
- ✅ Basic connectivity checks
- ⏱️ Runs in ~5 seconds

#### 3. **Full Test Suite** (Complete)
```bash
python run_tests.py --category all
```
- ✅ All unit tests
- ✅ Performance tests
- ✅ Coverage reports
- ⏱️ Runs in ~30 seconds

## 🚀 Quick Start

### 1. Install Test Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Quick Tests
```bash
python run_tests.py
```

### 3. Run All Tests
```bash
python run_tests.py --category all
```

## 📊 Test Coverage

The tests cover:

### ✅ **Data Buffer Tests**
- Data buffer updates
- Buffer size limits
- Trade/bar handlers
- Symbol processing

### ✅ **Feature Engineering Tests**
- Feature generation with sufficient data
- Handling insufficient data
- Data preprocessing

### ✅ **Trading Strategy Tests**
- Buy/sell signal generation
- Model predictions
- Risk calculations

### ✅ **Risk Management Tests**
- Position size calculations
- Stop-loss calculations
- Take-profit calculations

### ✅ **Market Hours Tests**
- Market open/closed detection
- Forex 24/7 trading capability
- API error handling

### ✅ **Logging Tests**
- Log file creation
- Log directory setup
- Log message formatting

### ✅ **Model Loading Tests**
- Model file loading
- Scaler file loading
- Error handling

## 🔧 Running Specific Tests

### Run Individual Test Classes
```bash
# Data buffer tests
python -m unittest test_trading_agent.TestDataBuffer

# Trading strategy tests
python -m unittest test_trading_agent.TestTradingStrategy

# Risk management tests
python -m unittest test_trading_agent.TestRiskManagement
```

### Run with Pytest (More Features)
```bash
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests with coverage
pytest --cov=trading_agent_core --cov=trading_agent_main

# Run specific test file
pytest test_market_hours.py -v

# Run tests matching pattern
pytest -k "buffer" -v
```

## 🐛 Debugging Tests

### Verbose Output
```bash
python run_tests.py --verbose
```

### Run Single Test
```bash
python -m unittest test_trading_agent.TestDataBuffer.test_update_data_buffer -v
```

### Check Test Coverage
```bash
pytest --cov=trading_agent_core --cov-report=html
# Open htmlcov/index.html in browser
```

## 📈 Performance Tests

The test suite includes performance benchmarks:

```bash
python test_trading_agent.py
```

This will show:
- Data buffer update performance
- Feature generation speed
- Memory usage patterns

## 🛠️ Test Configuration

### Pytest Configuration (`pytest.ini`)
- Coverage reporting enabled
- HTML and XML reports
- Test markers for categorization
- Verbose output by default

### Test Markers
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.performance` - Performance tests

## 🔍 Common Test Issues

### 1. **Import Errors**
```bash
# Make sure you're in the correct directory
cd /path/to/trading_agent

# Install dependencies
pip install -r requirements.txt
```

### 2. **Model Files Missing**
```bash
# Check if model files exist
ls -la *.joblib

# If missing, you need to train the model first
```

### 3. **API Credentials**
```bash
# Tests use mock API calls, but check your credentials in trading_agent_main.py
```

### 4. **Streaming Issues**
```bash
# Run streaming tests separately
python test_stream.py
python test_stream_simple.py
```

## 📋 Test Checklist

Before running your trading agent 24/7, ensure:

- [ ] Quick tests pass: `python run_tests.py --category quick`
- [ ] Integration tests pass: `python run_tests.py --category integration`
- [ ] Streaming tests pass: `python test_stream.py`
- [ ] Market hours configured for forex: `python test_market_hours.py`
- [ ] All unit tests pass: `python run_tests.py --category all`

## 🚨 Important Notes

### **Mock vs Real Tests**
- Most tests use mocks to avoid real API calls
- Streaming tests may make actual connections
- Performance tests use real data processing

### **Test Data**
- Tests use synthetic data for consistency
- No real trading occurs during tests
- Model predictions are mocked

### **Coverage**
- Aim for >80% code coverage
- Focus on critical trading logic
- Test error conditions thoroughly

## 🔄 Continuous Testing

### Pre-commit Tests
```bash
# Run before making changes
python run_tests.py --category quick
```

### Daily Tests
```bash
# Run comprehensive tests daily
python run_tests.py --category all
```

### Performance Monitoring
```bash
# Monitor performance over time
python test_trading_agent.py
```

## 📞 Troubleshooting

### Test Failures
1. Check error messages carefully
2. Verify dependencies are installed
3. Ensure model files exist
4. Check API credentials

### Performance Issues
1. Monitor memory usage
2. Check for memory leaks
3. Optimize data structures
4. Profile slow functions

### Coverage Issues
1. Add tests for uncovered code
2. Focus on critical paths
3. Test error conditions
4. Mock external dependencies

---

**Remember: Always run tests before deploying your trading agent to production!** 