build_type=${1:-Debug}
build_dir=build/${build_type,,}

cmake -B "$build_dir" -GNinja -DCMAKE_BUILD_TYPE=$build_type \
     -DDOWNLOAD_BOOST=1 -DWITH_BOOST=~/boost

time ninja -C "$build_dir"
