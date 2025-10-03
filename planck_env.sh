
# Source this after building PLC (clik)
export CLIK_PATH="<PLC_ROOT>/install"
export DYLD_LIBRARY_PATH="$CLIK_PATH/lib:${DYLD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="$CLIK_PATH/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="$CLIK_PATH/lib/python${PYTHONPATH:+:$PYTHONPATH}"
echo "Set CLIK_PATH=$CLIK_PATH"
