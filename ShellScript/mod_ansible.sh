
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
#!/bin/bash
#
# This code is ansible module example using bash.
 
function exit_json() {
    if [ -n "$2" ] ; then
        json_structure="
            {
                \"changed\": $1,
                $2
            }
        "
    else
        json_structure="
            {
                \"changed\": $1
            }
        "
    fi
    echo $json_structure
    exit 0
}
 
function fail_json() {
    json_structure="
        {
            \"failed\": "true",
            \"msg\": \"$1\"
        }
    "
    echo $json_structure
    exit 1
}
 
function main() {
    # arg parse
    arg_flag=0
    for arg in $(cat $1) ; do
        echo $arg | grep -E ',|\[|\]' > /dev/null 2>&1
        if [ $? -eq 0 ] ; then
            arg2="$arg2$arg"
            arg_flag=1
            continue
        fi
 
        if [ $arg_flag -eq 0 ] ; then
            key=`echo $arg | cut -d '=' -f 1`
            value=`echo $arg | cut -d '=' -f 2`
            declare "module_arg_$key=$value"
            arg_flag=0
        else
            key=`echo $arg2 | cut -d '=' -f 1`
            value=`echo $arg2 | cut -d '=' -f 2`
            declare "module_arg_$key=$value"
            arg_flag=0
        fi
    done
 
    # parameters
    name=$module_arg_name
    path=$module_arg_path
    state=$module_arg_state
 
    # When state is present
    if [ $state == "present" -a -n "$name" -a -n "$path" ] ; then
        if [ -d $path ] ; then
            if [ -d "$path/$name" ] ; then
                exit_json "false"
            else
                result=`mkdir "$path/$name" 2>&1`
                if [ -n "$result" ] ; then
                    fail_json "`echo -n $result`"
                else
                    exit_json "true" "\"directory_path\": \"$path/$name\""
                fi
            fi
        else
            fail_json "Error: not found $module_arg_path"
        fi
    fi
 
    # When state is absent
    if [ $state == "absent" -a -n "$name" -a -n "$path" ] ; then
        if [ -d "$path/$name" ] ; then
            rm -rf "$path/$name" 2>&1 > /dev/null
            if [ -d "$path/$name" ] ; then
                fail_json "Error: failed delete folder $path/$name"
            fi
            exit_json "true" "\"directory_path\": \"$path/$name\""
        else
            exit_json "false"
        fi
    fi
 
    fail_json "Required parameters include: name, path, state"
}
 
main $1
