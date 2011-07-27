<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a> &gt; New Sale</div>
		
		<h2>New Sale</h2>
		
		<form class="standard" action="/new-sale-detail.php">
			<label for="form-crop">Crop</label>
			<select id="form-crop">
				<option>Tomatoes</option>
				<option>Potato</option>
				<option>Onion</option>
			</select>
			
			<input type="submit" name="submit" class="submit" value="Continue &raquo;" />
			
		</form>		
		
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>