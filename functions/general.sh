#!/bin/bash

# setup clean log files
setupLogs(){
    rm -f log.txt
    rm -f prime.txt
    touch log.txt
}

# output help
helpText(){
    echo ""
    usageText
    echo ""
    echo "-l                number of test loops to perform (default: 1)"
    echo "-t                'cores' tests all cores"
    echo "                  'threads' tests all threads (default: cores)"
    echo "-b                number of browsers to launch (default: 2) (0 to skip test)"
    echo "--first-half      tests the first half of the cores/threads (skips 7z tests)"
    echo "--second-half     tests the second half of the cores/threads (skips 7z tests)"
    echo "--help            show this help menu"
    echo ""
    echo "Additional test settings can be found in settings.sh"
    echo ""
}

# output usage help
usageText(){
    echo "Usage: $0 [-l loops] [-t type (cores|threads)] [-b number of browsers] [--second-half] [--first-half]"
}

# startup logo
startupAscii(){
    echo -e "\033[0;31m"                                                       
    echo "                                ▒▒                                "
    echo "                                ▓▓                                "
    echo "                                ▓▓▓▓                              "
    echo "                                ████                              "
    echo "                              ░░████                              "
    echo "                              ██▓▓██                              "
    echo "                        ░░  ████▓▓▓▓    ▒▒                        "
    echo "                        ▓▓▒▒▓▓██▒▒▓▓  ██░░                        "
    echo "                      ▓▓██████▒▒▓▓▒▒████  ▒▒                      "
    echo "                      ██████▒▒▒▒▓▓▒▒██▒▒  ██                      "
    echo "                      ██▓▓▓▓░░▒▒████▓▓░░▒▒██  ░░                  "
    echo "                      ██▒▒▒▒░░▒▒▓▓██▓▓▓▓████▓▓░░                  "
    echo "                      ██▒▒▒▒░░▒▒████▓▓██▓▓████░░                  "
    echo "                      ██▒▒░░░░▒▒▓▓██▒▒██▒▒██▓▓░░                  "
    echo "                  ░░  ▒▒▒▒░░░░░░▒▒██░░▒▒▒▒▓▓██                    "
    echo "                    ██▓▓▓▓░░  ░░▒▒▒▒░░░░▒▒▓▓▓▓                    "
    echo "                    ░░██▓▓▒▒░░  ░░░░░░░░░░▓▓░░                    "
    echo "                      ░░▓▓░░░░        ░░▒▒░░                      "
    echo "                          ░░▒▒░░      ░░                          "                                                               
    echo "#  ................................................................."
    echo "#  ▗▄▄▄▖▗▖.▗▖▗▄▄▖.▗▄▄▄▖.▗▄▖.▗▄▄▄..▗▄▄▖▗▄▄▄▖▗▄▄▄▖▗▄▄▖.▗▄▄▖.▗▄▄▄▖▗▄▄▖."
    echo "#  ..█..▐▌.▐▌▐▌.▐▌▐▌...▐▌.▐▌▐▌..█▐▌.....█..▐▌...▐▌.▐▌▐▌.▐▌▐▌...▐▌.▐▌"
    echo "#  ..█..▐▛▀▜▌▐▛▀▚▖▐▛▀▀▘▐▛▀▜▌▐▌..█.▝▀▚▖..█..▐▛▀▀▘▐▛▀▘.▐▛▀▘.▐▛▀▀▘▐▛▀▚▖"
    echo "#  ..█..▐▌.▐▌▐▌.▐▌▐▙▄▄▖▐▌.▐▌▐▙▄▄▀▗▄▄▞▘..█..▐▙▄▄▖▐▌...▐▌...▐▙▄▄▖▐▌.▐▌"
    echo "#  ................................................................."
    echo ""
    echo "WARNING: SAVE ALL WORK AND CLOSE ALL OTHER PROGRAMS NOW!"
    echo ""
    echo "Press Ctrl+C to exit tests at any time"
    echo "For more information use: ./thredstepper --help"
    echo -e "\033[0m"
}

# check dependencies
checkDeps(){
    # 7zip
    if check_installed "7z" ; then
        echo "$(tput setaf 2)7zip dependancy is met$(tput sgr0)"
    else
        echo "$(tput setaf 1)7zip is not installed!$(tput sgr0)"
        exit 1
    fi
    # stress-ng
    if check_installed "stress-ng" ; then
        echo "$(tput setaf 2)stress-ng dependancy is met$(tput sgr0)"
    else
        echo "$(tput setaf 1)stress-ng is not installed!$(tput sgr0)"
        exit 1
    fi
    echo ""
}
check_installed() {
    command -v "$1" &>/dev/null
}

# output selected options and settings
outputOptions(){
    # input options
    echo "Options" | tee -a log.txt
    echo "$(tput setaf 5)Loops: ${loops:-Not specified} $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Type: ${type:-Not specified} $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Browsers: ${browsers:-Not specified} $(tput sgr0)" | tee -a log.txt
    if [ "$first_half" == true ]; then 
        echo "$(tput setaf 5)First half: true $(tput sgr0)" | tee -a log.txt
    fi
    if [ "$second_half" == true ]; then
        echo "$(tput setaf 5)Second half: true $(tput sgr0)" | tee -a log.txt
    fi
    # settings
    echo ""
    echo "Test Settings" | tee -a log.txt
    echo "$(tput setaf 5)Light time: ${light_time} $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Medium time: ${medium_time} $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Heavy time: ${heavy_time} $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Prime time: ${all_core_time}s $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Rapid tests: ${rapid_tests} $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Rapid time: ${rapid_time} $(tput sgr0)" | tee -a log.txt
    echo "$(tput setaf 5)Rest time: ${rest_time}s $(tput sgr0)" | tee -a log.txt
    echo ""
    echo "STARTING TESTS IN $rest_time SECONDS..."
    echo ""
    sleep $rest_time
}

# cleanup exit of program
cleanup() {
    if [[ -z "$CLEANED_UP" ]]; then
        CLEANED_UP=1
        echo "$(tput setaf 5)---- Stopping tests and cleaning up $(tput sgr0)" | tee -a log.txt
        pkill stress
        pkill 7z
        stopBrowserTest
        exit
    fi
}