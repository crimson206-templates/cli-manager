# META: {"backend":"supercli_backend","source_cli":"supercli_backend","wrapper_cli":"supercli_backend"}
_supercli_backend_dd335f68b4aa246c_complete()
{
    local cur script coms opts com
    COMPREPLY=()
    _get_comp_words_by_ref -n : cur words

    # for an alias, get the real script behind it
    if [[ $(type -t ${words[0]}) == "alias" ]]; then
        script=$(alias ${words[0]} | sed -E "s/alias ${words[0]}='(.*)'/\1/")
    else
        script=${words[0]}
    fi

    # lookup for command
    for word in ${words[@]:1}; do
        if [[ $word != -* ]]; then
            com=$word
            break
        fi
    done

    # completing for an option
    if [[ ${cur} == --* ]] ; then
        opts="--ansi --help --no-ansi --no-interaction --quiet --verbose --version"

        case "$com" in

            (add)
            opts="${opts} "
            ;;

            (completion-init)
            opts="${opts} --wrapper"
            ;;

            (completion-refresh)
            opts="${opts} "
            ;;

            (help)
            opts="${opts} "
            ;;

            (list)
            opts="${opts} "
            ;;

        esac

        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
        __ltrim_colon_completions "$cur"

        return 0;
    fi

    # completing for a command
    if [[ $cur == $com ]]; then
        coms="add completion-init completion-refresh help list"

        COMPREPLY=($(compgen -W "${coms}" -- ${cur}))
        __ltrim_colon_completions "$cur"

        return 0
    fi
}

complete -o default -F _supercli_backend_dd335f68b4aa246c_complete supercli_backend
complete -o default -F _supercli_backend_dd335f68b4aa246c_complete /home/crimson/miniconda3/envs/editting/bin/supercli_backend
