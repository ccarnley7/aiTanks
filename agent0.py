















<!doctype html>
<!-- paulirish.com/2008/conditional-stylesheets-vs-css-hacks-answer-neither/ -->
<!--[if lt IE 7 ]> <html class="no-js ie6" lang="en"> <![endif]-->
<!--[if IE 7 ]>    <html class="no-js ie7" lang="en"> <![endif]-->
<!--[if IE 8 ]>    <html class="no-js ie8" lang="en"> <![endif]-->
<!--[if (gte IE 9)|!(IE)]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">

    <title>Brigham Young University Sign-in Service</title>
    <meta name="description" content="">
    <meta name="author" content="">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script type="text/javascript" src="/cas/js/jquery/1.4.2/jquery.min.js;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1"></script>
    <script type="text/javascript" src="/cas/js/jquery/1.8.5/jquery-ui.min.js;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1"></script>
    <link rel="shortcut icon" href="/cas/images/favicon.ico;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1"/>
    <link rel="stylesheet" media="all and (min-width: 1px) and (max-width: 550px)" href="/cas/css/handheld.css;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1" />
    <link rel="stylesheet" media="all and (min-width: 550px)" href="/cas/css/style.css;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1"/>
    <link rel="stylesheet" media="all" href="/cas/css/application.css;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1"/>
    <script type="text/javascript" src="/cas/js/cas.js;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1"></script>
	<script type="text/javascript" src="/cas/js/modernizr/modernizr.custom.js;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1"></script>
</head>

<body>
   <!--Content-->
   <div id="main" class="content" role="main">
        <h2><div id="BYU"></div><!--img src="/cas/images/BYUBar.png;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1" alt="BYU Brigham Young University" /--></h2>

<form id="credentials" action="/cas/login;jsessionid=C20CC2E72737ECDB9B4FEA508EF2F5CB.1?service=https%3A%2F%2Flearningsuite.byu.edu%2Fplugins%2FUpload%2FfileDownload.php%3FfileId%3Ddb678010-9dzh-NAGX-VKpp-nR1f50d48690" method="post" onsubmit="return sanitizeNetID()">
	
	<h1>Sign In</h1>
	<fieldset id="inputarea">
		<div class="row">
			<label for="netid" id="labelnetid"><span class="accesskey">N</span>et ID:</label>
			
			
				
				<input id="netid" name="username" tabindex="1" accesskey="n" type="text" value="" autocomplete="true"/>
			
		</div>
		<div class="row">
			<label for="password" id="labelpassword"><span class="accesskey">P</span>assword:</label>
			
			<input id="password" name="password" tabindex="2" accesskey="p" type="password" value="" autocomplete="true"/>
		</div>
		<div id="warngroup" class="row">
			<input name="warn" value="true" id="warn" tabindex="3"
				   accesskey="w" type="checkbox"/>
			<label for="warn" id="warnlabel"><span class="accesskey">W</span>arn me before signing me into other sites.</label>
		</div>
		<input type="hidden" name="execution" value="e1s1"/>
		<input type="hidden" name="lt" value="LT-558177-v2rWcyla2oaOsLR5CGiuW5jQ7OTwx1"/>
		<input type="hidden" name="_eventId" value="submit"/>
		<input type="submit" class="submit" tabindex="4" value=""/>
	</fieldset>
</form>
<div id="links">
	<a href="https://y.byu.edu/ae/prod/authentication/cgi/findNetId.cgi" id="forgot">Forgot your Net ID or password?</a>
	<br>
	<a href="https://y.byu.edu/ae/prod/person/cgi/createNetId.cgi" id="create">Create a Net ID</a>
</div>
<div id="security" class="content" role="main">
	<div id="lock"></div>
	<p><strong>Security:</strong> BYU protects personal information by restricting network access to individuals with an
		authorized username and password. The username is a unique, personal network identifier called a Net ID
		and is assigned to each BYU patron.</p>

	<p>For security reasons, please sign out and Exit your web browser when you are finished accessing authenticated services!</p>
</div>



<script type="text/javascript">
  if (!String.prototype.trim) {
    (function() {
      // Make sure we trim BOM and NBSP
      var rtrim = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g;
      String.prototype.trim = function() {
        return this.replace(rtrim, '');
      };
    })();
  }

  var sanitizeNetID = function() {
    var netIDElement = document.getElementById('netid');
    netIDElement.value = netIDElement.value.trim().toLowerCase();
    return true;
  };
</script>







</div>
<div id="powered-by">
    <p>&sdot; <i>Powered by</i> BYU Office of Information Technology Core Services &sdot;</p>
</div>
<script type="text/javascript">

    var _gaq = _gaq || [];
    _gaq.push(['_setAccount', 'UA-17149951-3']);
    _gaq.push(['_trackPageview']);

    (function () {
        var ga = document.createElement('script');
        ga.type = 'text/javascript';
        ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(ga, s);
    })();

</script>
</body>
</html>

