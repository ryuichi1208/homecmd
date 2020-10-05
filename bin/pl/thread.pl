    use threads ('yield',
                 'stack_size' => 64*4096,
                 'exit' => 'threads_only',
                 'stringify');

    sub start_thread {
        my @args = @_;
        print('Thread started: ', join(' ', @args), "\n");
    }
    my $thr = threads->create('start_thread', 'argument');
    $thr->join();

    threads->create(sub { print("I am a thread\n"); })->join();

    my $thr2 = async { foreach (@files) { ... } };
    $thr2->join();
    if (my $err = $thr2->error()) {
        warn("Thread error: $err\n");
    }

    # Invoke thread in list context (implicit) so it can return a list
    my ($thr) = threads->create(sub { return (qw/a b c/); });
    # or specify list context explicitly
    my $thr = threads->create({'context' => 'list'},
                              sub { return (qw/a b c/); });
    my @results = $thr->join();

    $thr->detach();

    # Get a thread's object
    $thr = threads->self();
    $thr = threads->object($tid);

    # Get a thread's ID
    $tid = threads->tid();
    $tid = $thr->tid();
    $tid = "$thr";

    # Give other threads a chance to run
    threads->yield();
    yield();

    # Lists of non-detached threads
    my @threads = threads->list();
    my $thread_count = threads->list();

    my @running = threads->list(threads::running);
    my @joinable = threads->list(threads::joinable);

    # Test thread objects
    if ($thr1 == $thr2) {
        ...
    }

    # Manage thread stack size
    $stack_size = threads->get_stack_size();
    $old_size = threads->set_stack_size(32*4096);

    # Create a thread with a specific context and stack size
    my $thr = threads->create({ 'context'    => 'list',
                                'stack_size' => 32*4096,
                                'exit'       => 'thread_only' },
                              \&foo);

    # Get thread's context
    my $wantarray = $thr->wantarray();

    # Check thread's state
    if ($thr->is_running()) {
        sleep(1);
    }
    if ($thr->is_joinable()) {
        $thr->join();
    }

    # Send a signal to a thread
    $thr->kill('SIGUSR1');

    # Exit a thread
    threads->exit();
