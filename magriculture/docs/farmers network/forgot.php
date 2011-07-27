<?php include_once('header.php'); ?>

	<div class="h2">Recover Password</div>
	
	<div class="content">
		<form class="recover" action="/forgotsuccess.php">
		
			<label for="form-cell">Cell number</label>
			<input type="tel" id="form-cell" />
			
			<label for="form-question">Secret Question Label?</label>
			<input type="text" id="form-question" />
			
			<input type="submit" class="submit" value="Send Password &raquo;" name="submit" />
			<input type="submit" class="submit" value="Cancel &raquo;" name="cancel" />
			
			<p><a href="/help.php">Contact us for help</a></p>
		</form>
		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>