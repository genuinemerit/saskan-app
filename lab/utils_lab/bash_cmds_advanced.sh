#!/bin/bash
# #!/bin/bash -v
# #!/bin/bash -vx
# Include -v -x for verbose output.
# -v lists the line before executing it.
# -x lists each command before executing it.
#
# See showenvs.sh for a lot of basic environmental variables and some basic env commands
#
# Syntax tips
# ========================
echo -e "\nBasic syntax tips"
echo -e "==================="
echo -e "Use \\ to escape stuff"
echo -e "BASH has no concat symbol. Just run stuff together on a line."
echo -e "echo -e adds a line break at start of line and interprets '\\\n' OK."
echo -e "Variable values can be included inside of quotes. Also see printf."
echo -e "\nA variable is declared locally just stating it, like:\t\t\tMYVAR=23"
echo -e "It is referenced by prefixing it with a $ like:\t\t\t\techo \$MYVAR"
echo -e "\nCast a command to an unnamed variable by enclosing it like this:\t\$(mycmd)"
echo -e "This is a handy way to get the value from a command, e.g.:\t\tMYDIR=\$(pwd)"
echo -e "Cast a complex command to an unnamed variable using curly braces:\t\${..stuff..}"
echo -e "Braces (curly brackets) also unabmiguously identify a variable:\t\t\${MYVAR}"
echo -e "\nA function is declared like this:\t\t\t\t\tfuncname () { }"
echo -e "And a called just like any other command:\t\t\t\tfuncname"
echo -e "\nTo construct conditional logic:\t\t\t\t\tif.. then .. else/elif ... fi"
echo -e "Enclose conditions in double square brackets:\t\t\tif [[ \$test == 'something' ]]"
echo -e "Enclose arithmetic operations in double parens:\t\t\tRES=(( 23 * ( 2 + 5) ))"
#
# Test for vulnerabilities
# ========================
echo -e "\nVulnerability tests"
echo -e "====================="
#
# Shell-shock vulnerability 1. This should display just the word "test":
test1=$(env 'x=() { :;}; echo vulnerable''BASH_FUNC_x()=() { :;}; echo vulnerable' bash -c "echo test")
if [[ $test1 == "test" ]]
then
    echo -e "Shell-shock test 1 passed OK"
else
    echo -e "Shell-shock test 1 failed"
fi
#
# Shell-shock vulnerability 2.
# This should display the word date followed by "cat: /tmp/echo: No such file or directory"
thisdir=$(pwd)
cd /tmp; rm -f /tmp/echo; env 'x=() { (a)=>\' bash -c "echo date"; cat /tmp/echo
echo -e "if you are seeing 'cat: /tmp/echo: No such file or directory' then Shell-shock test 2 passed OK"
cd $thisdir
#
# Understanding the nature of commands: use type
# ==============================================
echo -e "\n'type' identifies the nature of commands"
echo -e "==========================================="
echo -e "type ls:\n\n$(type ls)\n"
echo -e "type -a ls:\n\n$(type -a ls)\n"
echo -e "type -t ls:\n\n$(type -t ls)\n"
echo -e "type -a pwd:\n\n$(type -a pwd)\n"
echo -e "type -t pwd:\n\n$(type -t pwd)\n"
quote () {
    local quoted=${1//\'/\'\\\'\'};
    printf "'%s'" "$quoted"
}
echo -e "type ls quote pwd do id\n\n$(type ls quote pwd do id)\n"
quote Hola
quote "Hello world"
quote Hello,+cruel+bash+world!
echo -e
echo -e "Doing 'type' is an easy and handy way to determine if your cool new script name already exists."
#
# Messing with the PATH
# =================================
echo -e "\nPATH and HOME"
echo -e "================================="
echo -e "Append a dir to PATH using a colon:\t\t\t\t:"
echo -e "Add current dir to PATH using a dot:\t\t\$ export PATH=\$PATH:."
echo -e "\$HOME is the same as ~/"
echo -e "echo \${HOME}:\t\t${HOME}"
echo -e "echo \$(echo ~/):\t"$(echo ~/)
echo -e "echo \${PATH}:\t"${PATH}
echo -e "A reasonable strategy for building up specialized commands is to put them in ~/bin"
#
# Configuring Nano
# ========================
echo -e "\nConfiguring and Using Nano"
echo -e "================================="
echo -e "I am not much of a fan of vi/vim."
echo -e "On using nano, see: https://nano-editor.org/dist/v2.2/nano.html"
echo -e "To configure nano, see: https://www.nano-editor.org/dist/v2.1/nanorc.5.html"
echo -e "The nano config file goes in ~/.nanorc"
echo -e "Nano uses Ctrl- (^) and Alt- (M-, referredt to as 'Meta') keys for special functions and toggles."
echo -e "All the most common ones are displayed at bottom of the editor. ^-G for Help."
echo -e "You can modify nano settings when launching it, eg 'nano -t whatever' autosaves on exit."
echo -e "In ~/.nanonrc, do 'set tempfile' to make that the default."
echo -e "A handy Meta-command is Alt-/, which takes you the last line.  Alt-\\ goes to first line."
#
# Making things executable
# =============================
echo -e "\nManaging executables and return codes"
echo -e "======================================="
echo -e "Along with using ~/bin, chmod is your friend. Note that chmod +x is easier to remember than chmod 777"
echo -e "Do cmd2 only if cmd1 FAILS:\t\t\t\$ cmd1 || cmd2"
echo -e "Do cmd2 only if cmd1 SUCCEEDS:\t\t\t\$ cmd1 && cmd2"
echo -e "\$? holds the exit code, aka the return code"
echo -e "Provide an explicit exit code using the 'exit' command."
#
# Arguments
# ==============================
echo -e "\nArguments and Quotes"
echo -e "============================"
echo -e "\$0 is the name of the script itself."
echo -e "\$1, \$2, .. \$9 are the enumerated positional arguments 1 thru 9."
echo -e "\${10}, \${11}, .. for positional arguments beyond number 9."
echo -e "\$# is a count of the number of arguments."
echo -e "\$* references all of the arguments."
echo -e "Double quotes allow the use of embedded variables, require escapes for var-related markers."
echo -e "Single quotes do not expand variables, no not requre escapes."
#
# BATS
# ===============================
echo -e "\nBATS: Bash Automated Testing System"
echo -e "====================================="
echo -e "For installation and basic usage, see: https://github.com/sstephenson/bats"
echo -e "For a somewhat nicer tutorial/guide, see: https://blog.engineyard.com/2014/bats-test-command-line-tools"
echo -e "It installs bats under/usr/local/bin so make sure that is in your PATH"
