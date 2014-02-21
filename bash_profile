# Include HomeBrew install path
export PATH="/usr/local/bin:/usr/local/sbin:$PATH"

# Include TeX
export PATH="/usr/texbin:$PATH"

## PyEnv
#if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi
#export PATH="/Users/jmcarp/code/pyenv/bin:$PATH"
#eval "$(pyenv init -)"

# Virtualenvwrapper
export WORKON_HOME=~/env
source /usr/local/bin/virtualenvwrapper.sh

# Postgres APP
export PATH="/Applications/Postgres.app/Contents/MacOS/bin:$PATH"

### Added by the Heroku Toolbelt
export PATH="/usr/local/heroku/bin:$PATH"
