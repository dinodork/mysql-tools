build_type=${1:-Debug}
build_dir=build/${build_type,,}.clang

cmake -B "$build_dir" -GNinja -DCMAKE_BUILD_TYPE=$build_type \
     -DDOWNLOAD_BOOST=1 -DWITH_BOOST=~/boost \
     -DCMAKE_C_COMPILER=clang-18 -DCMAKE_CXX_COMPILER=clang++-18 \
     -DWITH_AUTHENTICATION_LDAP=0 -DWITH_PERCONA_AUTHENTICATION_LDAP=0 \
     -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DFORCE_COLORED_OUTPUT=ON

time ninja -C "$build_dir"
