<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a> &gt; Add Note</div>
		
		<div class="h2">Add A Note</div>
		
		<form class="standard" action="/new-sale-success.php">
			<label for="form-note">Note <span>[200 characters left]</span></label>
			<textarea rows="4" cols="30" id="form-note"></textarea>
			<input type="submit" name="submit" class="submit" value="Add Note &raquo;" />
			<input type="submit" name="cancel" class="submit" value="cancel" />
		</form>		
		
		<div class="h2">Menu</div>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>