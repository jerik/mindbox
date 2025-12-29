" Test runner for mindbox.vim
" Run with: vim -Nu NONE -n -es -S test/run.vim

" Add repo root to runtimepath
let s:repo_root = fnamemodify(expand('<sfile>:p:h'), ':h')
execute 'set runtimepath+=' . s:repo_root

" Source the plugin
execute 'source ' . s:repo_root . '/plugin/mindbox.vim'

" Source all test files
for s:test_file in glob(s:repo_root . '/test/test_*.vim', 0, 1)
  execute 'source ' . s:test_file
endfor

" Report results
let s:result_file = '/tmp/vim_test_result.txt'
if len(v:errors) > 0
  call writefile(['FAILED'] + v:errors, s:result_file)
  cquit
else
  call writefile(['PASSED: All tests passed!'], s:result_file)
  qa
endif
