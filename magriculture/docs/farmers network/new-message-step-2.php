<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a> &gt; New Sale</div>
		
		<h2>Compose Message</h2>
		
		<form class="standard" action="">
			<label for="form-message">Message <span>[160 characters left]</span></label>
			<textarea rows="4" id="form-message"></textarea>
			<p>Recipients: Group Name 1, Group name 2, Group name 3</p>
		
			<input type="submit" name="submit" class="submit" value="Send Message &raquo;" />
			<input type="submit" name="cancel" class="submit" value="cancel" />
			
		</form>		
		
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>