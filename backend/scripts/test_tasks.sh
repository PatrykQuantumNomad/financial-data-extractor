#!/bin/bash

# Script to test Celery tasks via the API
# Usage: ./scripts/test_tasks.sh [command] [options]

set -e

# Detect if terminal supports colors
if [ -t 1 ] && command -v tput > /dev/null 2>&1; then
    # Terminal supports colors
    COLOR_SUPPORT=true
    RED=$(tput setaf 1)
    GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3)
    BLUE=$(tput setaf 4)
    CYAN=$(tput setaf 6)
    BOLD=$(tput bold)
    NC=$(tput sgr0) # No Color
else
    # Terminal doesn't support colors or not a TTY
    COLOR_SUPPORT=false
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Alternative: check for NO_COLOR environment variable (standard)
if [ -n "${NO_COLOR}" ]; then
    COLOR_SUPPORT=false
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Default API URL
API_URL="${API_URL:-http://localhost:3000}"
BASE_URL="${API_URL}/api/v1/tasks"

# Function to print colored output
# Note: All user-facing messages go to stderr so they don't interfere with stdout captures
print_info() {
    echo -e "${CYAN}ℹ${NC} $1" >&2
}

print_success() {
    echo -e "${GREEN}✓${NC} $1" >&2
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1" >&2
}

print_header() {
    if [ "${COLOR_SUPPORT}" = "true" ]; then
        echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
        echo -e "${BLUE}$1${NC}" >&2
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n" >&2
    else
        echo -e "\n============================================================" >&2
        echo -e "$1" >&2
        echo -e "============================================================\n" >&2
    fi
}

# Function to check if API is available
check_api() {
    if ! curl -s -f "${API_URL}/health" > /dev/null 2>&1 && ! curl -s -f "${API_URL}/" > /dev/null 2>&1; then
        print_error "API is not available at ${API_URL}"
        print_info "Make sure the FastAPI server is running: make run"
        exit 1
    fi
}

# Function to trigger a task and return task_id
trigger_task() {
    local endpoint=$1
    local method="${2:-POST}"

    print_info "Triggering task: ${endpoint}"

    response=$(curl -s -X "${method}" \
        -H "Content-Type: application/json" \
        "${BASE_URL}${endpoint}")

    if [ $? -ne 0 ]; then
        print_error "Failed to trigger task"
        return 1
    fi

    # Extract task_id from response
    task_id=$(echo "${response}" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)

    if [ -z "${task_id}" ]; then
        print_error "Failed to get task_id from response:"
        echo "${response}" | jq '.' 2>/dev/null || echo "${response}" >&2
        return 1
    fi

    print_success "Task triggered successfully"
    echo -e "${CYAN}Task ID:${NC} ${task_id}" >&2
    # Output task_id to stdout for capture (only this line goes to stdout)
    echo "${task_id}"
    return 0
}

# Function to get task status
get_task_status() {
    local task_id=$1

    print_info "Checking status for task: ${task_id}"

    response=$(curl -s -X GET "${BASE_URL}/${task_id}")

    if [ $? -ne 0 ]; then
        print_error "Failed to get task status"
        return 1
    fi

    # Pretty print JSON if jq is available, otherwise just show response
    if command -v jq &> /dev/null; then
        echo "${response}" | jq '.'
    else
        echo "${response}"
    fi

    # Extract status
    status=$(echo "${response}" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    case "${status}" in
        "PENDING"|"STARTED"|"PROGRESS")
            echo -e "${YELLOW}Status: ${status}${NC}" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}Status: ${status}${NC}" >&2
            ;;
        "FAILURE")
            echo -e "${RED}Status: ${status}${NC}" >&2
            ;;
        *)
            echo -e "${CYAN}Status: ${status}${NC}" >&2
            ;;
    esac

    return 0
}

# Function to poll task status
poll_task() {
    local task_id=$1
    local max_wait=${2:-300}  # Default 5 minutes
    local interval=${3:-2}    # Default 2 seconds

    print_info "Polling task status (max wait: ${max_wait}s, interval: ${interval}s)"

    elapsed=0
    while [ ${elapsed} -lt ${max_wait} ]; do
        response=$(curl -s -X GET "${BASE_URL}/${task_id}")
        status=$(echo "${response}" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

        case "${status}" in
            "SUCCESS")
                print_success "Task completed successfully!"
                echo "${response}" | jq '.' 2>/dev/null || echo "${response}"
                return 0
                ;;
            "FAILURE")
                print_error "Task failed!"
                echo "${response}" | jq '.' 2>/dev/null || echo "${response}"
                return 1
                ;;
            "PENDING"|"STARTED"|"PROGRESS")
                echo -ne "\r${CYAN}Waiting... (${elapsed}s/${max_wait}s) Status: ${status}${NC}" >&2
                sleep ${interval}
                elapsed=$((elapsed + interval))
                ;;
            *)
                echo -e "\n${YELLOW}Unknown status: ${status}${NC}" >&2
                echo "${response}" | jq '.' 2>/dev/null || echo "${response}" >&2
                return 1
                ;;
        esac
    done

    echo -e "\n" >&2
    print_warning "Timeout waiting for task to complete"
    get_task_status "${task_id}"
    return 2
}

# Company-level tasks
test_company_extract() {
    local company_id=$1
    print_header "Testing: Extract Company Financial Data"

    task_id=$(trigger_task "/companies/${company_id}/extract")
    if [ $? -eq 0 ] && [ -n "${task_id}" ]; then
        if [ "${POLL:-false}" = "true" ]; then
            poll_task "${task_id}" 7200 5  # 2 hours max, check every 5s
        else
            get_task_status "${task_id}"
        fi
    fi
}

test_company_scrape() {
    local company_id=$1
    print_header "Testing: Scrape Investor Relations"

    task_id=$(trigger_task "/companies/${company_id}/scrape")
    if [ $? -eq 0 ] && [ -n "${task_id}" ]; then
        if [ "${POLL:-false}" = "true" ]; then
            poll_task "${task_id}" 600 3  # 10 minutes max, check every 3s
        else
            get_task_status "${task_id}"
        fi
    fi
}

test_company_recompile() {
    local company_id=$1
    print_header "Testing: Recompile Company Statements"

    task_id=$(trigger_task "/companies/${company_id}/recompile")
    if [ $? -eq 0 ] && [ -n "${task_id}" ]; then
        if [ "${POLL:-false}" = "true" ]; then
            poll_task "${task_id}" 1800 3  # 30 minutes max, check every 3s
        else
            get_task_status "${task_id}"
        fi
    fi
}

# Document-level tasks
test_document_process() {
    local document_id=$1
    print_header "Testing: Process Document End-to-End"

    task_id=$(trigger_task "/documents/${document_id}/process")
    if [ $? -eq 0 ] && [ -n "${task_id}" ]; then
        if [ "${POLL:-false}" = "true" ]; then
            poll_task "${task_id}" 3600 3  # 1 hour max, check every 3s
        else
            get_task_status "${task_id}"
        fi
    fi
}

test_document_download() {
    local document_id=$1
    print_header "Testing: Download PDF"

    task_id=$(trigger_task "/documents/${document_id}/download")
    if [ $? -eq 0 ] && [ -n "${task_id}" ]; then
        if [ "${POLL:-false}" = "true" ]; then
            poll_task "${task_id}" 300 2  # 5 minutes max, check every 2s
        else
            get_task_status "${task_id}"
        fi
    fi
}

test_document_classify() {
    local document_id=$1
    print_header "Testing: Classify Document"

    task_id=$(trigger_task "/documents/${document_id}/classify")
    if [ $? -eq 0 ] && [ -n "${task_id}" ]; then
        if [ "${POLL:-false}" = "true" ]; then
            poll_task "${task_id}" 120 2  # 2 minutes max, check every 2s
        else
            get_task_status "${task_id}"
        fi
    fi
}

test_document_extract() {
    local document_id=$1
    print_header "Testing: Extract Financial Statements"

    task_id=$(trigger_task "/documents/${document_id}/extract")
    if [ $? -eq 0 ] && [ -n "${task_id}" ]; then
        if [ "${POLL:-false}" = "true" ]; then
            poll_task "${task_id}" 1800 3  # 30 minutes max, check every 3s
        else
            get_task_status "${task_id}"
        fi
    fi
}

# Show usage
show_usage() {
    if [ "${COLOR_SUPPORT}" = "true" ]; then
        cat << EOF
${CYAN}Celery Task Testing Script${NC}

${GREEN}Usage:${NC}
    $0 <command> [options]

${GREEN}Commands:${NC}
    ${YELLOW}company-scrape${NC} <company_id>      Scrape investor relations website
    ${YELLOW}company-extract${NC} <company_id>     Full extraction workflow
    ${YELLOW}company-recompile${NC} <company_id>   Recompile statements

    ${YELLOW}doc-process${NC} <document_id>        Process document end-to-end
    ${YELLOW}doc-download${NC} <document_id>       Download PDF
    ${YELLOW}doc-classify${NC} <document_id>      Classify document
    ${YELLOW}doc-extract${NC} <document_id>       Extract financial statements

    ${YELLOW}status${NC} <task_id>                 Check task status
    ${YELLOW}poll${NC} <task_id> [max_wait]       Poll task until completion

    ${YELLOW}help${NC}                             Show this help message

${GREEN}Options:${NC}
    ${YELLOW}POLL=true${NC}                        Auto-poll task status after triggering
                                                   Example: POLL=true $0 company-scrape 1

    ${YELLOW}API_URL=<url>${NC}                    Override API URL
                                                   Example: API_URL=http://localhost:8000 $0 status abc123

${GREEN}Examples:${NC}
    # Trigger scraping task
    $0 company-scrape 1

    # Trigger and poll until completion
    POLL=true $0 company-scrape 1

    # Check task status
    $0 status a00d8c65-c7fd-4360-8f4c-836b0df25f59

    # Poll task status
    $0 poll a00d8c65-c7fd-4360-8f4c-836b0df25f59 600

${GREEN}Environment:${NC}
    API_URL=${API_URL}
    Base URL: ${BASE_URL}

EOF
    else
        cat << EOF
Celery Task Testing Script

Usage:
    $0 <command> [options]

Commands:
    company-scrape <company_id>      Scrape investor relations website
    company-extract <company_id>     Full extraction workflow
    company-recompile <company_id>   Recompile statements

    doc-process <document_id>        Process document end-to-end
    doc-download <document_id>       Download PDF
    doc-classify <document_id>      Classify document
    doc-extract <document_id>       Extract financial statements

    status <task_id>                 Check task status
    poll <task_id> [max_wait]       Poll task until completion

    help                             Show this help message

Options:
    POLL=true                        Auto-poll task status after triggering
                                     Example: POLL=true $0 company-scrape 1

    API_URL=<url>                    Override API URL
                                     Example: API_URL=http://localhost:8000 $0 status abc123

Examples:
    # Trigger scraping task
    $0 company-scrape 1

    # Trigger and poll until completion
    POLL=true $0 company-scrape 1

    # Check task status
    $0 status a00d8c65-c7fd-4360-8f4c-836b0df25f59

    # Poll task status
    $0 poll a00d8c65-c7fd-4360-8f4c-836b0df25f59 600

Environment:
    API_URL=${API_URL}
    Base URL: ${BASE_URL}

EOF
    fi
}

# Main script logic
main() {
    check_api

    case "${1:-help}" in
        company-scrape|scrape)
            if [ -z "$2" ]; then
                print_error "Company ID required"
                echo "Usage: $0 company-scrape <company_id>"
                exit 1
            fi
            test_company_scrape "$2"
            ;;
        company-extract|extract)
            if [ -z "$2" ]; then
                print_error "Company ID required"
                echo "Usage: $0 company-extract <company_id>"
                exit 1
            fi
            test_company_extract "$2"
            ;;
        company-recompile|recompile)
            if [ -z "$2" ]; then
                print_error "Company ID required"
                echo "Usage: $0 company-recompile <company_id>"
                exit 1
            fi
            test_company_recompile "$2"
            ;;
        doc-process|process)
            if [ -z "$2" ]; then
                print_error "Document ID required"
                echo "Usage: $0 doc-process <document_id>"
                exit 1
            fi
            test_document_process "$2"
            ;;
        doc-download|download)
            if [ -z "$2" ]; then
                print_error "Document ID required"
                echo "Usage: $0 doc-download <document_id>"
                exit 1
            fi
            test_document_download "$2"
            ;;
        doc-classify|classify)
            if [ -z "$2" ]; then
                print_error "Document ID required"
                echo "Usage: $0 doc-classify <document_id>"
                exit 1
            fi
            test_document_classify "$2"
            ;;
        doc-extract|extract-doc)
            if [ -z "$2" ]; then
                print_error "Document ID required"
                echo "Usage: $0 doc-extract <document_id>"
                exit 1
            fi
            test_document_extract "$2"
            ;;
        status)
            if [ -z "$2" ]; then
                print_error "Task ID required"
                echo "Usage: $0 status <task_id>"
                exit 1
            fi
            print_header "Task Status"
            get_task_status "$2"
            ;;
        poll)
            if [ -z "$2" ]; then
                print_error "Task ID required"
                echo "Usage: $0 poll <task_id> [max_wait_seconds]"
                exit 1
            fi
            max_wait=${3:-300}
            print_header "Polling Task Status"
            poll_task "$2" "${max_wait}"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
