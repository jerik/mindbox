" Tests for mindbox.vim plugin

let s:repo_root = fnamemodify(expand('<sfile>:p:h'), ':h')

" Test: Plugin loaded correctly
function! s:test_plugin_loaded() abort
  call assert_true(exists(':MindboxList'), 'MindboxList command should exist')
  call assert_true(exists(':Mindbox'), 'Mindbox command should exist')
  call assert_true(exists(':MindboxSearch'), 'MindboxSearch command should exist')
endfunction

" Test: MindboxList with test directory
function! s:test_mindbox_list() abort
  let test_dir = tempname() . '/mindboxes'
  call mkdir(test_dir, 'p')
  call writefile(['*mindbox-test* test'], test_dir . '/test.mb')
  let g:mindbox_directory = test_dir

  redir => output
  silent MindboxList
  redir END

  call assert_match('test', output, 'MindboxList should show test')

  call delete(test_dir, 'rf')
  unlet g:mindbox_directory
endfunction

" Test: Mindbox opens topic
function! s:test_mindbox_open() abort
  let test_dir = tempname() . '/mindboxes'
  call mkdir(test_dir, 'p')
  call writefile(['*mindbox-sample* sample', 'content here'], test_dir . '/sample.mb')
  let g:mindbox_directory = test_dir

  silent Mindbox sample

  call assert_equal('help', &buftype, 'Buffer should have help buftype')
  call assert_match('sample\.mb', expand('%'), 'Should open sample.mb')

  bwipeout!
  call delete(test_dir, 'rf')
  unlet g:mindbox_directory
endfunction

" Test: Mindbox with invalid topic shows error
function! s:test_mindbox_invalid() abort
  let test_dir = tempname() . '/mindboxes'
  call mkdir(test_dir, 'p')
  let g:mindbox_directory = test_dir

  let v:errmsg = ''
  silent! Mindbox nonexistent

  call assert_match('not found', v:errmsg, 'Should show error for invalid topic')

  call delete(test_dir, 'rf')
  unlet g:mindbox_directory
endfunction

" Test: Empty directory shows message
function! s:test_empty_directory() abort
  let test_dir = tempname() . '/empty'
  call mkdir(test_dir, 'p')
  let g:mindbox_directory = test_dir

  redir => output
  silent MindboxList
  redir END

  call assert_match('No mindbox topics', output, 'Should show no topics message')

  call delete(test_dir, 'rf')
  unlet g:mindbox_directory
endfunction

" Run all tests
call s:test_plugin_loaded()
call s:test_mindbox_list()
call s:test_mindbox_open()
call s:test_mindbox_invalid()
call s:test_empty_directory()
