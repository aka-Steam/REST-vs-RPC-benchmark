#!/bin/bash
# Bash script to run Locust benchmark tests
# Usage:
#   ./scripts/run_benchmark.sh rest sanity
#   ./scripts/run_benchmark.sh grpc stress --headless

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
SERVICE=""
SCENARIO=""
HEADLESS=false
CONFIG_FILE="config/test_scenarios.yaml"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        rest|grpc)
            SERVICE="$1"
            shift
            ;;
        sanity|normal|stress|stability)
            SCENARIO="$1"
            shift
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 <rest|grpc> <sanity|normal|stress|stability> [--headless] [--config <file>]"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$SERVICE" ] || [ -z "$SCENARIO" ]; then
    echo -e "${RED}Error: Service and scenario are required${NC}"
    echo "Usage: $0 <rest|grpc> <sanity|normal|stress|stability> [--headless]"
    exit 1
fi

# Function to get config from YAML using Python
get_config() {
    python3 -c "
import yaml
import sys
import json

with open('$CONFIG_FILE', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

scenario = config['scenarios']['$SCENARIO']
service = config['services']['$SERVICE']
output = config['output']

result = {
    'scenario': scenario,
    'service': service,
    'output': output
}

print(json.dumps(result))
"
}

# Function to check service health
check_service_health() {
    local service_type=$1
    local host=$2
    
    if [ "$service_type" = "rest" ]; then
        if curl -s -f "${host}/health" > /dev/null 2>&1; then
            return 0
        else
            return 1
        fi
    elif [ "$service_type" = "grpc" ]; then
        local hostname=$(echo $host | cut -d: -f1)
        local port=$(echo $host | cut -d: -f2)
        if nc -z "$hostname" "${port:-50051}" 2>/dev/null; then
            return 0
        else
            return 1
        fi
    fi
    return 1
}

# Main script
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Locust Benchmark Test Runner${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not available${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}Python: $PYTHON_VERSION${NC}"

# Check if Locust is installed
if ! python3 -m locust --version &> /dev/null; then
    echo -e "${RED}Error: Locust is not installed${NC}"
    echo "Run: pip install -r requirements_benchmark.txt"
    exit 1
fi

LOCUST_VERSION=$(python3 -m locust --version 2>&1)
echo -e "${GREEN}Locust: $LOCUST_VERSION${NC}"

# Check if PyYAML is available
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${YELLOW}Warning: PyYAML not found. Installing...${NC}"
    pip install pyyaml
fi

# Load configuration
echo -e "${YELLOW}Loading configuration from $CONFIG_FILE...${NC}"
CONFIG_JSON=$(get_config)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to load configuration${NC}"
    exit 1
fi

# Extract configuration values (using Python for JSON parsing)
SCENARIO_NAME=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario']['name'])")
SERVICE_NAME=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['service']['name'])")
DESCRIPTION=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario']['description'])")
USERS=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario']['users'])")
SPAWN_RATE=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario']['spawn_rate'])")
DURATION=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario']['duration'])")
LOCUSTFILE=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['service']['locustfile'])")
HOST=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['service']['host'])")
USER_CLASS=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['service']['user_class'])")
OUTPUT_DIR=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['output']['base_dir'])")
CSV_PREFIX=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print('true' if json.load(sys.stdin)['output']['csv_prefix'] else 'false')")
HTML_REPORT=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print('true' if json.load(sys.stdin)['output']['html_report'] else 'false')")

echo ""
echo -e "${CYAN}Test Configuration:${NC}"
echo -e "  Service: ${SERVICE_NAME}"
echo -e "  Scenario: ${SCENARIO_NAME}"
echo -e "  Description: ${DESCRIPTION}"
echo -e "  Users: ${USERS}"
echo -e "  Spawn Rate: ${SPAWN_RATE} users/sec"
echo -e "  Duration: ${DURATION}"
echo ""

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"
if check_service_health "$SERVICE" "$HOST"; then
    echo -e "${GREEN}Service is healthy!${NC}"
else
    echo -e "${YELLOW}Warning: Service at $HOST appears to be unavailable${NC}"
    echo -e "${YELLOW}Please ensure the service is running before starting the test${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Prepare output directory
OUTPUT_PATH="${OUTPUT_DIR}/${SERVICE}/${SCENARIO}"
mkdir -p "$OUTPUT_PATH"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CSV_PREFIX_PATH="${OUTPUT_PATH}/${SERVICE}_${SCENARIO}_${TIMESTAMP}"

# Build Locust command
LOCUST_ARGS=("-f" "$LOCUSTFILE")

if [ "$SERVICE" = "rest" ]; then
    LOCUST_ARGS+=("-H" "$HOST")
fi

if [ "$HEADLESS" = true ]; then
    LOCUST_ARGS+=("--headless" "-u" "$USERS" "-r" "$SPAWN_RATE" "-t" "$DURATION")
fi

if [ "$CSV_PREFIX" = "true" ]; then
    LOCUST_ARGS+=("--csv" "$CSV_PREFIX_PATH")
fi

if [ "$HTML_REPORT" = "true" ]; then
    HTML_FILE="${OUTPUT_PATH}/${SERVICE}_${SCENARIO}_${TIMESTAMP}.html"
    LOCUST_ARGS+=("--html" "$HTML_FILE")
fi

if [ -n "$USER_CLASS" ]; then
    LOCUST_ARGS+=("$USER_CLASS")
fi

echo -e "${CYAN}Starting Locust test...${NC}"
echo -e "Command: python3 -m locust ${LOCUST_ARGS[*]}"
echo ""

# Run Locust
if python3 -m locust "${LOCUST_ARGS[@]}"; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Test completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${CYAN}Results saved to: $OUTPUT_PATH${NC}"
    
    if [ "$CSV_PREFIX" = "true" ]; then
        echo -e "${CYAN}CSV files:${NC}"
        ls -1 "${CSV_PREFIX_PATH}"*.csv 2>/dev/null | while read file; do
            echo -e "  - $(basename $file)"
        done
    fi
    
    if [ "$HTML_REPORT" = "true" ]; then
        echo -e "${CYAN}HTML report: $HTML_FILE${NC}"
    fi
else
    EXIT_CODE=$?
    echo ""
    echo -e "${YELLOW}Test completed with exit code: $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi

