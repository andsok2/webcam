#!/usr/bin/perl

use strict;
use warnings;
use CGI "param";
use Digest::SHA "sha256_base64";

###
### Subroutine declarations
###


###
### Main logic
###

our $mandate_path = '/tmp/webcam/mandates.txt';
our $session_path = '/tmp/webcam/sessions.txt';
our $user_path = 'webcam_users.txt'; 	# these are permanent, cannot reside in tmp, 
										# will hold them in work dir

# incoming parameters
my $user_inc = param('user');
my $pass_inc = param('pass');
my $sess_inc = param('sess');
my $action = param('action');

if(!($sess_inc || $user_inc))
{
	show_login();
}
elsif($sess_inc)
{
	my $session_status = session_valid($sess_inc);
	if($session_status eq 'valid') 
	{
		if($action eq 'logout')
		{
			remove_session($sess_inc);
			show_login();
		}
		else
		{
			update_session($sess_inc); # shift expiration time by 1 hour from now
			show_main($sess_inc); 	# supply session id to 
									# include in output
		}
	}
	elsif($session_status eq 'expired')
	{
		remove_session($sess_inc);
		show_login('Session expired.');
	}
	else
	{
		show_login();
	}
}
elsif($user_inc && $pass_inc)
{
	if(user_valid($user_inc, $pass_inc))
	{
		my $sess = random(24);
		save_session($sess);
		show_main($sess);	# session id supplied 
							# to include in output
	}
	else
	{
		show_login('Wrong credentials'); # error message supplied
	}
}
else
{
	show_login();
}

###
###Subroutine definitions
###
sub session_valid
{
	my $sid = shift;
	my %s_hash = read_sessions();
	if(exists $s_hash{$sid})
	{
		if( time() <= $s_hash{$sid})
		{
			return 'valid';
		}
		else
		{
			return 'expired';
		}
	}
	else
	{
		return 0;
	}
}

sub read_sessions
{
	my %s_hash;
	open(my $sfh, '<', $session_path) or die "Cannot open $session_path $!\n";
	flock( $sfh, 1);
	while(my $line = <$sfh>)
	{
		chomp $line;
		my ($session, $timeout) = split(':', $line);
		$s_hash{$session} = $timeout;
	}
	close $sfh;
	return %s_hash;
}
sub save_sessions
{
	my %s_hash = @_;
	open(my $sfh, '>', $session_path) or die "Cannot open $session_path $!\n";
	flock( $sfh, 2);
	foreach my $session (keys %s_hash)
	{
		print $sfh "$session:$s_hash{$session}\n"
	}
	close $sfh;
}

sub update_session
{
	my $sid = shift;
	my %s_hash = read_sessions();
	
	$s_hash{$sid} += 3600;
	
	save_sessions(%s_hash);
}

sub remove_session
{
	my $sid = shift;
	my %s_hash = read_sessions();
	
	my $found = delete $s_hash{$sid};
	die "session not found" if (!$found);
	
	save_sessions(%s_hash);
}

sub user_valid
{
	my $uname_inc = shift;
	my $passw_inc = shift;
	open(my $ufh, '<', $user_path) or die "Cannot open $user_path $!\n";
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

sub save_session
{
	my $sid = shift;
	my $timeout = 3600 + time(); 
	open (my $sfh, '>>', $session_path) or die "Cannot open $session_path $!\n";
	flock ($sfh, 2); #exclusive lock
	print $sfh "$sid:$timeout\n";
	close $sfh;
}

sub random
{
	my $length = shift;
	my @const = (0..9,'a'..'z','A'..'Z'); # 62 elements, index from 0 to 61
	my @rand = ();
	foreach my $i (0..$length-1)
	{
		$rand[$i] = $const[int(rand(62))];
	}
	return join('',@rand);
}

sub show_main
{
	my $sess_id = shift;
	my $mandate = random(16);
	save_mandate($mandate);
	
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
sub save_mandate
{
	my $mandate = shift @_;
	open (my $mfh, '>>', $mandate_path) or 
		die "Cannot open file '$mandate_path' $!";
	flock($mfh, 2);
	print $mfh "$mandate\n";
	close $mfh;
}

