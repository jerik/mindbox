if exists('g:loaded_mindbox_plugin')
  finish
endif
let g:loaded_mindbox_plugin = 1

let s:repo_root = expand('<sfile>:p:h:h:h')
let s:default_dir = s:repo_root . '/mindboxes'

function! s:mindbox_dir() abort
  return expand(get(g:, 'mindbox_directory', s:default_dir))
endfunction

function! s:topic_files() abort
  return sort(globpath(s:mindbox_dir(), '*.mb', 0, 1))
endfunction

function! s:topics() abort
  return map(copy(s:topic_files()), 'fnamemodify(v:val, ":t:r")')
endfunction

function! s:mindbox_resolve(topic) abort
  let file = s:mindbox_dir() . '/' . a:topic . '.mb'
  return filereadable(file) ? file : ''
endfunction

function! s:open_topic(topic) abort
  if empty(a:topic)
    echo "Mindbox: provide a topic (use :MindboxList to inspect)."
    return
  endif
  let file = s:mindbox_resolve(a:topic)
  if empty(file)
    echoerr 'Mindbox topic not found: ' . a:topic
    return
  endif
  execute 'silent keepalt topleft new'
  execute 'silent keepalt edit ' . fnameescape(file)
  setlocal buftype=help filetype=help bufhidden=wipe nobuflisted noswapfile
  setlocal nomodifiable
  nnoremap <buffer> <silent> q :close<CR>
endfunction

function! s:list_topics() abort
  let topics = s:topics()
  if empty(topics)
    echo 'No mindbox topics found in ' . s:mindbox_dir()
    return
  endif
  echo 'Mindbox topics:'
  for topic in topics
    echom '  ' . topic
  endfor
endfunction

function! s:complete_topics(A, L, P) abort
  return filter(copy(s:topics()), 'v:val =~? "^" . escape(a:A, "\\")')
endfunction

function! s:search(pattern) abort
  if empty(a:pattern)
    echo 'MindboxSearch: provide a pattern'
    return
  endif
  let files = s:topic_files()
  if empty(files)
    echo 'No mindbox files to search'
    return
  endif
  let escaped = escape(a:pattern, '/\\')
  execute 'silent vimgrep /' . escaped . '/gj ' . join(map(copy(files), 'fnameescape(v:val)'), ' ')
  copen
endfunction

command! MindboxList call s:list_topics()
command! -nargs=? -complete=customlist,s:complete_topics Mindbox call s:open_topic(<q-args>)
command! -nargs=+ MindboxSearch call s:search(<q-args>)
