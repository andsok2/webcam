package Menu;

use strict;
use warnings;
use Session;

sub show_main
{
        my $sess_id = shift;
        my $mandate = &Session::random(16);
        &Session::save_mandate($mandate);

        my $head = "Content-type: text/html\n\n";
        my $html = <<"HTML_END";
<!DOCTYPE html
        PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
<head>
        <title>Webcam</title>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
</head>
<body>
        <div id="logout">
                <form method="post" action="webcam.cgi" enctype="multipart/form-data">
                        <input type="hidden" name="sess" value="$sess_id"  />
                        <input type="hidden" name="action" value="logout"  />
                        <input type="submit" name="submit" value="Logout" />
                </form>
        </ div>
        <div id="image">
                <img src='image.cgi?mandate=$mandate'>
                <form method="post" action="webcam.cgi" enctype="multipart/form-data">
                        <input type="hidden" name="sess" value="$sess_id"  />
                        <input type="hidden" name="action" value="refresh"  />
                        <input type="submit" name="submit" value="Refresh" />
                </form>
        </ div>
</body>
</html>
HTML_END

        print $head;
        print $html;
}


1;
