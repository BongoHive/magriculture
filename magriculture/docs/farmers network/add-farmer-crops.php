<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a></div>
		
		<div class="h2">Select Crops</div>
		
		<form class="standard" action="">
			<label for="form-crops">Top Crops in District</label>
			<select multiple="multiple" size="2" id="form-crops">
				<option>Tomatoes</option>
				<option>Potatoes</option>
				<option>Onions</option>
			</select>
			<input type="submit" name="submit" class="submit" value="Add to Farmer &raquo;" />
			
			<a href="/add-farmer-crops-search.php">Search for other crops not in list</a>
			
		</form>
		
		<div class="h2">Menu</div>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>