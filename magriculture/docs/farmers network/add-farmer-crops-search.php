<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a></div>
		
		<div class="h2">Search Crops</div>
		
		<form class="standard" action="">
			<input type="text" />
			<input type="submit" name="submit" class="submit" value="Search &raquo;" />
		</form>
		
		<form class="standard" action="">
			<select multiple="multiple" size="2" id="form-crops">
				<option>Red Cabbage</option>
				<option>Potatoes</option>
				<option>Onions</option>
				<option>Tomatoes</option>
				<option>Potatoes</option>
				<option>Onions</option>
			</select>
			<input type="submit" name="submit" class="submit" value="Add to Farmer &raquo;" />
		</form>
		
		<div class="h2">Menu</div>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>