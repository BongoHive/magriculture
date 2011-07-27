<?php include_once('header.php'); ?>

	<h2>Sign In</h2>
	
	<form class="signin" action="/home.php">
		<div class="error">Sign in failed.<br />Please try again.</div>
	
		<label for="form-cell">Cell number</label>
		<input type="tel" id="form-cell" />
		
		<label for="form-pin">Pin</label>
		<input type="password" id="form-pin" />
		
		<input type="submit" class="submit" value="Sign In &raquo;" name="submit" />
		
		<p><a href="/forgot.php">Forgotton your Pin?</a></p>
	</form>
		
<?php include_once('footer.php'); ?>