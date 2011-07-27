<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a> &gt; New Sale</div>
		
		<div class="h2">New Sale</div>
		
		<form class="standard" action="/new-sale-detail.php">
			<label for="form-crop">Crop</label>
			<select id="form-crop">
				<option>Tomatoes</option>
				<option>Potato</option>
				<option>Onion</option>
			</select>
			
			<input type="submit" name="submit" class="submit" value="Continue &raquo;" />
			
		</form>		
		
		<div class="h2">Menu</div>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>