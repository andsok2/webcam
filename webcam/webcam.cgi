#!/usr/bin/perl

use strict;
use warnings;
use CGI "param";
use Constants;
use Login;
use Session;
use Menu;

###
### Main logic
###

# incoming parameters
my $user_inc = param('user');
my $pass_inc = param('pass');
my $sess_inc = param('sess');
my $action = param('action');

if(!($sess_inc || $user_inc))
{
	&Login::show_login();
}
elsif($sess_inc)
{
	my $session_status = &Session::session_valid($sess_inc);
	if($session_status eq 'valid') 
	{
		if($action eq 'logout')
		{
			&Session::remove_session($sess_inc);
			&Login::show_login();
		}
		else
		{
			&Session::update_session($sess_inc); # shift expiration time by 1 hour from now
			&Menu::show_main($sess_inc); 	# supply session id to 
									# include in output
		}
	}
	elsif($session_status eq 'expired')
	{
		&Session::remove_session($sess_inc);
		&Login::show_login('Session expired.');
	}
	else
	{
		&Login::show_login();
	}
}
elsif($user_inc && $pass_inc)
{
	if(&Login::user_valid($user_inc, $pass_inc))
	{
		my $sess = &Session::random(24);
		&Session::save_session($sess);
		&Menu::show_main($sess);	# session id supplied 
							# to include in output
	}
	else
	{
		&Login::show_login('Wrong credentials'); # error message supplied
	}
}
else
{
	&Login::show_login();
}


