<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a></div>
		
		<h2>Edit Farmer Details</h2>
		
		<form class="standard" action="">
			<label for="form-name">Name</label>
			<input type="text" id="form-name" value="Rupert" />
			
			<label for="form-surname">Surname</label>
			<input type="text" id="form-surname" value="de Villiers" />
			
			<label for="form-mobile">Mobile Number</label>
			<input type="text" id="form-mobile" value="082222222" />

			<label for="form-region">Region</label>
			<select id="form-region">
				<option>Stellenbosch</option>
				<option selected="selected">Paarl</option>
				<option>Cape Town</option>
			</select>
			
			<input type="submit" name="submit" class="submit" value="Update &raquo;" />
			<input type="submit" name="cancel" class="submit" value="cancel" />
			
			<a href="#">Change Farmer's crops</a>
			
		</form>	
			
			
			
		
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>