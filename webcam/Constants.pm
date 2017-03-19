package Constants;

use strict;
use warnings;

our $mandate_path = '/tmp/webcam/mandates.txt';
our $session_path = '/tmp/webcam/sessions.txt';
our $user_path = 'webcam_users.txt';    # these are permanent, cannot reside in tmp,
                                        # will hold them in work dir

our $tmp_dir_path = '/tmp/webcam';

1;
