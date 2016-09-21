package Login;

use strict;
use warnings;
use Digest::SHA "sha256_base64";
use Constants;
use Session;

sub user_valid
{
        my $uname_inc = shift;
        my $passw_inc = shift;
        open(my $ufh, '<', $Constants::user_path) or die "Cannot open $Constants::user_path $!\n";
        flock($ufh, 1);
        my $found = 0;
        while(my $line = <$ufh>)
        {
                chomp $line;
                my ($user, $password) = split(':', $line);
                if($user eq $uname_inc)
                {
                        if(sha256_base64($passw_inc) eq $password)
                        {
                                $found = 1;
                                last;
                        }
                }
        }
        close $ufh;
        return $found;
}


sub show_login
{
        my $error = shift || '';
        my $head = "Content-type: text/html\n\n";
        my $html = <<"HTML_END";
<!DOCTYPE html
        PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
<head>
        <title>Webcam Login</title>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
</head>
<body>
        <p id="error">$error</p>
        <form method="post" action="webcam.cgi" enctype="multipart/form-data">
                <input type="text" name="user" />
                <input type="password" name="pass" />
                <input type="submit" name="submit" value="Enter" />
        </form>
</body>
</html>
HTML_END

        print $head;
        print $html;
}


1;


